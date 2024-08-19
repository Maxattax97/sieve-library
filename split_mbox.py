#!/usr/bin/env python3

import mailbox
import os


def split_mbox_to_eml(mbox_file, output_dir):
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the MBOX file
    mbox = mailbox.mbox(mbox_file)

    # Iterate through the emails in the MBOX file
    for idx, message in enumerate(mbox):
        # Construct the output file path
        eml_file = os.path.join(output_dir, f"email_{idx+1:05d}.eml")

        # Write the message to an EML file
        with open(eml_file, "w") as f:
            f.write(message.as_string())

        print(f"Saved: {eml_file}")


# Split the MBOX into individual EML files
split_mbox_to_eml("./gmail_takeout.mbox", "./gmail/")
