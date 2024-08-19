#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from datetime import datetime, timezone
from email import message_from_file
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses, parseaddr
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from psycopg2.extras import execute_values
from queue import Queue
from threading import Thread
import email
import hashlib
import logging
import mailbox
import nltk
import os
import psycopg2
import re

logger = logging.getLogger(__name__)
logging.basicConfig(filename="sieve.log", encoding="utf-8", level=logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# Regex to remove script and style tags along with their content
REGEX_HTML_SCRIPTS = re.compile(r"(?is)<(script|style).*?>.*?</\1>")

# Regex to remove HTML tags
REGEX_HTML_TAGS = re.compile(r"<[^>]+>")

# Regex to remove HTML entities
# https://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references#Character_entity_references_in_HTML
REGEX_HTML_ENTITY = re.compile(r"&[a-zA-Z]+[0-9]*;")

# Regex to remove non-alphabet characters
REGEX_NON_WORDS = re.compile(r"[^a-zA-Z]+")

# Regex to remove extra whitespace
REGEX_EXTRA_WHITESPACE = re.compile(r"\s{2,}")

# Regex to remove the plus address part in an email address
REGEX_EMAIL_ADDRESS_PLUS = re.compile(r"(\+[^@]+)(?=@)")


class EmailProcessor:
    def __init__(
        self, db_config, dirty_dir="dirty", storage_dir="storage", max_workers=8
    ):
        self.conn = psycopg2.connect(**db_config)
        self.dirty_dir = dirty_dir
        self.storage_dir = storage_dir
        self.max_workers = max_workers
        self.stemmer = PorterStemmer()
        self.stop_words = None
        # self.preload_nltk_data()
        # self.drop_tables()
        # self.create_tables()

    def preload_nltk_data(self):
        """Preload NLTK data to avoid concurrency issues."""
        logger.info("Preloading NLTK data ...")
        nltk.download("punkt")
        nltk.download("stopwords")
        nltk.download("wordnet")

        # Force loading other NLTK resources
        self.stop_words = set(stopwords.words("english"))
        _ = nltk.word_tokenize("Test sentence to trigger loading.")
        _ = list(nltk.corpus.wordnet.all_synsets())
        logger.info("NLTK data preloaded")

    def drop_tables(self):
        """Drop all tables in the database."""
        with self.conn.cursor() as cursor:
            cursor.execute("DROP TABLE IF EXISTS emails CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS addresses CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS conversations CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS words CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS subject_occurrences CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS body_occurrences CASCADE;")
            self.conn.commit()

    def create_tables(self):
        """Create necessary tables in the database."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS emails (
                    id SERIAL PRIMARY KEY,
                    sha_hash TEXT UNIQUE NOT NULL,
                    last_updated TIMESTAMP WITH TIME ZONE NOT NULL
                );
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS addresses (
                    id SERIAL PRIMARY KEY,
                    address TEXT UNIQUE NOT NULL
                );
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    email_id INTEGER REFERENCES emails(id),
                    address_id INTEGER REFERENCES addresses(id),
                    PRIMARY KEY (email_id, address_id)
                );
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS words (
                    id SERIAL PRIMARY KEY,
                    word TEXT UNIQUE NOT NULL
                );
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS subject_occurrences (
                    id SERIAL PRIMARY KEY,
                    email_id INTEGER REFERENCES emails(id) ON DELETE CASCADE,
                    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
                    count INTEGER NOT NULL,
                    UNIQUE(email_id, word_id)
                );
            """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS body_occurrences (
                    id SERIAL PRIMARY KEY,
                    email_id INTEGER REFERENCES emails(id) ON DELETE CASCADE,
                    word_id INTEGER REFERENCES words(id) ON DELETE CASCADE,
                    count INTEGER NOT NULL,
                    UNIQUE(email_id, word_id)
                );
            """
            )
            self.conn.commit()

    def insert_email(self, sha_hash):
        """Insert an email into the database."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO emails (sha_hash, last_updated)
                VALUES (%s, %s)
                ON CONFLICT (sha_hash)
                DO UPDATE
                SET last_updated = EXCLUDED.last_updated
                RETURNING id;
            """,
                (sha_hash, datetime.now(timezone.utc).isoformat()),
            )
            self.conn.commit()
            return cursor.fetchone()[0]

    def insert_address(self, address):
        """Insert a address into the addresses table and return the address_id."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO addresses (address)
                VALUES (%s)
                ON CONFLICT (address) DO UPDATE
                SET address = EXCLUDED.address
                RETURNING id;
            """,
                (address,),
            )
            self.conn.commit()
            return cursor.fetchone()[0]

    def insert_conversation(self, email_id, address_id):
        """Insert a conversation into the conversations table."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO conversations (email_id, address_id)
                VALUES (%s, %s)
                ON CONFLICT (email_id, address_id) DO NOTHING;
            """,
                (email_id, address_id),
            )
            self.conn.commit()

    def insert_word(self, word):
        """Insert a word into the words table and return the word_id."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO words (word)
                VALUES (%s)
                ON CONFLICT (word) DO NOTHING;
            """,
                (word,),
            )
            self.conn.commit()
            cursor.execute("SELECT id FROM words WHERE word = %s", (word,))
            return cursor.fetchone()[0]

    def insert_words_batch(self, words):
        """Insert a batch of words into the words table and return their IDs."""
        with self.conn.cursor() as cursor:
            # Step 1: Attempt to insert the words
            insert_query = """
                INSERT INTO words (word)
                VALUES %s
                ON CONFLICT (word) DO NOTHING;
            """
            word_tuples = [(word,) for word in words]
            execute_values(cursor, insert_query, word_tuples)
            self.conn.commit()

            # Step 2: Select the IDs for all words (whether they were inserted or already existed)
            select_query = "SELECT id, word FROM words WHERE word = ANY(%s);"
            cursor.execute(select_query, (words,))
            word_id_map = {word: word_id for word_id, word in cursor.fetchall()}

            return word_id_map

    def insert_subject_occurrences_batch(self, occurrences):
        """Batch insert subject word occurrences."""
        with self.conn.cursor() as cursor:
            insert_query = """
                INSERT INTO subject_occurrences (email_id, word_id, count)
                VALUES %s
                ON CONFLICT (email_id, word_id) DO UPDATE
                SET count = subject_occurrences.count + EXCLUDED.count;
            """
            execute_values(cursor, insert_query, occurrences)
            self.conn.commit()

    def insert_subject_occurrence(self, email_id, word_id, count):
        """Insert a word occurrence into the occurrences table."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO subject_occurrences (email_id, word_id, count)
                VALUES (%s, %s, %s)
                ON CONFLICT (email_id, word_id) DO UPDATE
                SET count = subject_occurrences.count + EXCLUDED.count;
            """,
                (email_id, word_id, count),
            )
            self.conn.commit()

    def insert_body_occurrences_batch(self, occurrences):
        """Batch insert body word occurrences."""
        with self.conn.cursor() as cursor:
            insert_query = """
                INSERT INTO body_occurrences (email_id, word_id, count)
                VALUES %s
                ON CONFLICT (email_id, word_id) DO UPDATE
                SET count = body_occurrences.count + EXCLUDED.count;
            """
            execute_values(cursor, insert_query, occurrences)
            self.conn.commit()

    def insert_body_occurrence(self, email_id, word_id, count):
        """Insert a word occurrence into the occurrences table."""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO body_occurrences (email_id, word_id, count)
                VALUES (%s, %s, %s)
                ON CONFLICT (email_id, word_id) DO UPDATE
                SET count = body_occurrences.count + EXCLUDED.count;
            """,
                (email_id, word_id, count),
            )
            self.conn.commit()

    def get_email_object_by_id(self, email_id):
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT
                    e.id AS email_id,
                    e.sha_hash AS sha_hash,
                    e.last_updated AS last_updated,
                    -- Addresses
                    json_agg(DISTINCT a.address) AS addresses,
                    -- Subject words and counts
                    json_agg(DISTINCT jsonb_build_object('word', sw.word, 'count', so.count)) AS subject_words,
                    -- Body words and counts
                    json_agg(DISTINCT jsonb_build_object('word', bw.word, 'count', bo.count)) AS body_words
                FROM
                    emails e
                    -- Join conversations to get email addresses
                    LEFT JOIN conversations c ON e.id = c.email_id
                    LEFT JOIN addresses a ON c.address_id = a.id
                    -- Join subject occurrences and words
                    LEFT JOIN subject_occurrences so ON e.id = so.email_id
                    LEFT JOIN words sw ON so.word_id = sw.id
                    -- Join body occurrences and words
                    LEFT JOIN body_occurrences bo ON e.id = bo.email_id
                    LEFT JOIN words bw ON bo.word_id = bw.id
                WHERE
                    e.id = {email_id} -- Replace with the email ID you want to query
                GROUP BY
                    e.id
            """
            )
            self.conn.commit()
            return cursor.fetchall()

    # TODO: Convert this to thread + queue model
    def process_dirty(self):
        """Process .eml and .mbox files in the dirty directory."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for filename in os.listdir(self.dirty_dir):
                file_path = os.path.join(self.dirty_dir, filename)
                if filename.endswith(".eml"):
                    futures.append(executor.submit(self.store_eml_file, file_path))
                elif filename.endswith(".mbox"):
                    futures.append(executor.submit(self.store_mbox_file, file_path))

            for future in as_completed(futures):
                future.result()  # This will raise an exception if the thread raised one

    def store_eml_file(self, file_path):
        """Process a single .eml file."""
        with open(file_path, "r") as file:
            email_content = file.read()

        sha_hash = self.hash_email_content(email_content)
        storage_path = os.path.join(self.storage_dir, f"{sha_hash}.eml")

        if not os.path.exists(storage_path):
            with open(storage_path, "w") as file:
                file.write(email_content)

        # Remove the original dirty file
        os.remove(file_path)

    def store_mbox_file(self, file_path):
        """Process an .mbox file, splitting it into individual .eml files."""
        mbox = mailbox.mbox(file_path)
        for message in mbox:
            email_content = message.as_string()
            sha_hash = self.hash_email_content(email_content)
            storage_path = os.path.join(self.storage_dir, f"{sha_hash}.eml")

            if not os.path.exists(storage_path):
                with open(storage_path, "w") as file:
                    file.write(email_content)

        # Remove the original dirty file
        os.remove(file_path)

    def worker(self, queue):
        """Worker function that processes emails from the queue."""
        while True:
            file_path = queue.get()
            if file_path is None:
                break  # Exit the worker when None is received
            try:
                processor.process_email(file_path)
            finally:
                queue.task_done()

    def process_storage(self):
        """Process .eml files in the storage directory."""
        queue = Queue()
        workers = []

        # Enqueue tasks
        logger.info(f"Filling queue ...")
        for filename in os.listdir(self.storage_dir):
            file_path = os.path.join(self.storage_dir, filename)
            if filename.endswith(".eml"):
                queue.put(file_path)
        logger.info(f"Queue filled with {queue.qsize()} tasks")

        # Start worker threads
        logger.info(f"Starting {self.max_workers} workers ...")
        for _ in range(self.max_workers):
            thread = Thread(
                target=self.worker,
                args=(queue,),
            )
            thread.start()
            workers.append(thread)

        # Wait for all tasks to be completed
        queue.join()
        logger.info(f"All jobs complete")

        # Stop workers
        for _ in range(self.max_workers):
            queue.put(None)
        for worker in workers:
            worker.join()

    def hash_email_content(self, content):
        """Generate a SHA256 hash of the email content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def process_email(self, file_path):
        """Process a single .eml file."""
        try:
            with open(file_path, "rb") as file:
                msg = BytesParser(policy=policy.default).parse(file)

            # The sha hash is the name of the file:
            sha_hash = os.path.basename(file_path).replace(".eml", "")

            # Extract email addresses (from, to, cc, bcc)
            from_addresses = [msg["From"]]
            to_addresses = getaddresses(msg.get_all("To", []))
            cc_addresses = getaddresses(msg.get_all("Cc", []))
            bcc_addresses = getaddresses(msg.get_all("Bcc", []))

            # Flatten the address lists
            all_addresses = list(
                set(
                    from_addresses
                    + [addr[1] for addr in to_addresses + cc_addresses + bcc_addresses]
                )
            )

            # Get the email portion only, not the name
            all_addresses = [self.normalize_address(addr) for addr in all_addresses]
            # logger.debug(f"Extracted addresses: {all_addresses}")

            # Extract the subject
            subject = msg["Subject"] or ""
            norm_subject = self.normalize_content(subject)
            # logger.debug(f"Extracted to normalized subject: '{subject}' -> {norm_subject}")

            # Extract the body (assuming the email has both plain text and HTML parts)
            body = self.extract_body(msg)
            # logger.debug(f"Extracted body: {body}")
            norm_body = self.normalize_content(body)
            # logger.debug(f"Normalized body: {norm_body}")

            self.submit_email_parts(sha_hash, all_addresses, norm_subject, norm_body)
        except Exception as e:
            logger.error(f"Error processing {file_path}, skipping it:", e)

    def extract_body(self, msg):
        """Extracts the body from an email message, preferring plain text."""
        parts = []

        if msg.is_multipart():
            # Recursively process each part
            for part in msg.iter_parts():
                parts.append(self.extract_body(part))
        else:
            # Check if the content type is text/plain or text/html
            content_type = msg.get_content_type()
            if content_type in ("text/plain", "text/html"):
                # Decode the content and add to the parts list
                charset = msg.get_content_charset() or "utf-8"
                payload = msg.get_payload(decode=True).decode(charset, errors="replace")
                if content_type == "text/html" or content_type != "text/plain":
                    # Clean HTML content to be safe
                    payload = self.clean_html(payload)
                parts.append(payload)

        # Join all the parts into one long string
        return " ".join(parts)

    def clean_html(self, html_content):
        """Clean HTML content to extract plain text."""
        # Remove script and style tags along with their content
        html_content = re.sub(REGEX_HTML_SCRIPTS, " ", html_content)

        # Remove HTML tags
        html_content = re.sub(REGEX_HTML_TAGS, " ", html_content)

        # Remove HTML entities
        html_content = re.sub(REGEX_HTML_ENTITY, " ", html_content)

        return html_content

    def normalize_content(self, content):
        """Preprocess the email content (e.g., lowercasing, tokenization)."""
        if content is None:
            logger.warning("Content is None, skipping normalization")
            return []
        content = re.sub(REGEX_NON_WORDS, " ", content)
        content = re.sub(REGEX_EXTRA_WHITESPACE, " ", content)

        # Convert to lowercase
        content = content.lower()

        # Tokenize
        words = word_tokenize(content)

        # Remove short, or long words
        words = [word for word in words if len(word) >= 4 and (len(word) <= 16)]

        # Remove stopwords
        words = [word for word in words if word not in self.stop_words]

        # Make sure it's a valid word (in any language, slang, etc.) or is
        # word-like.
        words = [word for word in words if len(wordnet.synsets(word)) > 0]

        # Stemming
        words = [self.stemmer.stem(word) for word in words]
        return words

    def normalize_address(self, address):
        """Normalize an email address."""
        name, address = parseaddr(address)
        address = re.sub(REGEX_EMAIL_ADDRESS_PLUS, "", address)
        address = address.lower()
        return address

    def count_words(self, words):
        """Count the frequency of each word in the email content."""
        word_counts = {}
        for word in words:
            if word not in word_counts:
                word_counts[word] = 0
            word_counts[word] += 1
        return word_counts

    def submit_email_parts(self, sha_hash, n_addresses, n_subject, n_body):
        """Process the content of an email."""
        email_id = self.insert_email(sha_hash)

        # Insert addresses and conversations
        for address in n_addresses:
            address_id = self.insert_address(address)
            self.insert_conversation(email_id, address_id)

        # Process words for subjects and body
        subject_word_counts = self.count_words(n_subject)
        body_word_counts = self.count_words(n_body)

        all_words = set(subject_word_counts.keys()).union(set(body_word_counts.keys()))
        word_ids = self.insert_words_batch(list(all_words))

        # Batch insert subject occurrences
        subject_occurrences = [
            (email_id, word_ids[word], count)
            for word, count in subject_word_counts.items()
        ]
        self.insert_subject_occurrences_batch(subject_occurrences)

        # Batch insert body occurrences
        body_occurrences = [
            (email_id, word_ids[word], count)
            for word, count in body_word_counts.items()
        ]
        self.insert_body_occurrences_batch(body_occurrences)

        logger.info(
            f"Submitted email ID {email_id} {sha_hash}, {len(n_addresses)} addresses, {len(subject_word_counts)} subject words, {len(body_word_counts)} body words"
        )

    def close(self):
        """Close the database connection."""
        self.conn.close()


# Usage
db_config = {
    "dbname": "sieve",
    "user": "sieve",
    "password": "Fate9chap9priest",
    "host": "localhost",
    "port": "5432",
}

processor = EmailProcessor(db_config, max_workers=16)
# logger.info(processor.get_email_object_by_id(1))
# logger.info(processor.get_email_object_by_id(3))
# logger.info(processor.get_email_object_by_id(5000))
# processor.process_dirty()
# processor.process_storage()
processor.close()
