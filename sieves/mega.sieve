require ["fileinto", "imap4flags", "vnd.proton.expire", "variables"];
# require ["redirect"];

# If it's already marked as spam, ignore it and do no further processing.
if not header :is "X-Spam-Flag" "YES" {
  stop;
}

set "eva" "unset";

###########
# Flagged #
###########

if anyof (
    address :is "from" "artemchuk.tetiana@gmail.com",
    address :is "from" "alanrocull@gmail.com",
    address :is "from" "masteralan2001@gmail.com",
    address :is "from" "james.ocull@gmail.com",
    address :is "from" "houndeyex@gmail.com",
    address :is "from" "ldocull@gmail.com",
    address :is "from" "larry.ocull@ldo-systems.com",
    address :is "from" "larry.ocull@stryker.com",
    address :is "from" "wr9r.usa@stryker.com",
    address :is "from" "amocull@gmail.com",
    address :is "from" "hrocull@gmail.com",
    address :is "from" "hray.hc@gmail.com",
    address :is "from" "vips25@protonmail.com"
  )
{
  # This adds a star:
  addflag "\\Flagged";
  set "eva" "false";
}

###########
# Privacy #
###########

if address :domain "to" "passinbox.com" {
  # TODO: Flag as sensitive?
  set "eva" "false";
}


########
# Spam #
########

if anyof (
  header :contains "subject" "[itch.io]",
  address :is "to" "max.ocull+resy@protonmail.com"
) {
  fileinto "Spam";
  set "eva" "false";
}
elsif anyof (header :contains "subject" "Privacy Policy", header :contains "subject" "Terms of Service", header :contains "subject" "Legal Agreements", header :contains "subject" "Disclosure")
{
  fileinto "Trash";
  set "eva" "false";
}
elsif allof (address :is "from" "united.com", anyof (
    header :contains "subject" "entertainment options",
    header :contains "subject" "upcoming trip"
  )
) {
  fileinto "Trash";
  set "eva" "false";
}

############
# Software #
############

if allof (address :domain "from" "github.com")
{
  # Github
  fileinto "Software";
  set "eva" "false";
}
elsif anyof (
    address :is "from" "glsamaker@gentoo.com",
    address :is "from" "gentoo-announce@lists.gentoo.org"
  )
{
  fileinto "Software";
  expire "day" "7";
  set "eva" "false";
}


###########
# Finance #
###########

if anyof (
    address :contains "from" "nerdwallet",
    address :domain "from" "wealthfront.com",
    address :contains "from" "discover",
    address :contains "from" "teachers.creditunion",
    address :domain "from" "fidelity.com",
    address :contains "from" "chase",
    address :contains "from" "CenterPointEnergy",
    address :contains "from" "centerpoint.energy",
    address :domain "from" "centerpointenergy.com",
    address :domain "from" "duke-energyalert.com",
    address :contains "from" "huntington",
    address :domain "from" "venmo.com",
    address :domain "from" "mohela.studentaid.gov",
    header :contains "subject" "Payment confirmation",
    header :contains "subject" "Payment Received",
    address :domain "from" "notification.capitalone.com",
    header :contains "subject" "online bill is ready",
    address :domain "from" "interactivebrokers.com",
    allof (address :is "from" "service@sfmc.personalwealth.empower.com", header :contains "subject" "Your daily financial monitor")
) {
  fileinto "Finance";
  set "eva" "false";

  if anyof (
    header :contains "subject" "tax",
    header :contains "subject" "Tax"
  ) {
    fileinto "Special";
  }
  elsif anyof (
      header :contains "subject" "Thank you for your payment",
      header :contains "subject" "Payment confirmation",
      header :contains "subject" "Funds invested",
      header :contains "subject" "Payment Received"
  ) {
    fileinto "Receipts";
  }
  elsif anyof (
    header :contains "subject" "Scheduled transfer created",
    header :contains "subject" "scheduled transfer completed",
    header :contains "subject" "Transfer Has Been Scheduled",
    header :contains "subject" "A recent credit to your account",
    header :contains "subject" "deposit is available early",
    header :contains "subject" "IBKR FYI",
    header :contains "subject" "Changes in Analyst Ratings",
    header :contains "subject" "Message Center Notification",
    header :contains "subject" "Your Payment is Due Soon",
    header :contains "subject" "bill is ready",
    header :contains "subject" "payment has posted",
    header :contains "subject" "payment is scheduled",
    header :contains "subject" "mobile check deposit",
    header :contains "subject" "Automatic Payment",
    header :contains "subject" "Payment Alert - CenterPoint Energy",
    allof (
      address :domain "from" "chase.com",
      header :contains "subject" "transaction with"
    ),
    header :contains "subject" "payment reminder"
  ) {
    fileinto "Notification";
    expire "day" "3";
  }
  elsif anyof (
    header :contains "subject" "Your Monthly Statement is Available",
    header :contains "subject" "new statement",
    header :contains "subject" "Statement Available",
    header :contains "subject" "Review your recent activity",
    header :contains "subject" "No new alerts",
    header :contains "subject" "transaction history"
  ) {
    fileinto "Trash";
  }
}

# Schaaf CPA
if address :domain "from" "schaafcpa.com" {
  fileinto "Finance";
  fileinto "Special";

  # Adds a star
  addflag "\\Flagged";

  set "eva" "false";
}


##########
# Health #
##########
if anyof (
    header :contains "subject" "Your new Explanation of Benefits Summary"
  )
{
  fileinto "Trash";
  set "eva" "false";
}

##########
# Growth #
##########

if anyof (
    address :is "from" "alerts@chineseclass101.com",
    address :is "from" "indianapolisbjj@aol.com"
  )
{
  fileinto "Growth";
  set "eva" "false";
}

##########################
# Wordpress Auto Updates #
##########################

if anyof (
    header :contains "subject" "Some plugins were automatically updated",
    header :contains "subject" "Some plugins and themes have automatically updated",
    header :contains "subject" "Some themes were automatically updated"
  )
{
  fileinto "Trash";
  set "eva" "false";
}

##########
# Meetup #
##########

if allof (
    address :is "from" "info@meetup.com"
  )
{
  fileinto "Social";
  set "eva" "false";
}

#####################################
# Wealthfront Investment Prospectus #
#####################################

if allof (
    header :contains "subject" "Investment prospectus",
    address :contains "from" "wealthfront"
  )
{
  fileinto "Trash";
  set "eva" "false";
}

###########
# Surveys #
###########

if anyof (
    header :contains "subject" "Tell us how we did",
    header :contains "subject" "Survey Request",
    header :contains "subject" "feedback",
    header :contains "subject" "Feedback"
  )
{
  fileinto "Trash";
  set "eva" "false";
}

############
# Receipts #
############

if allof (address :domain "from" "ting.com", header :contains "subject" "bill has been paid")
{
  # Ting
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "info@myiclubonline.com", header :contains "subject" "Your online payment receipt")
{
  # Planet Fitness
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :domain "from" "pushpay.com", header :contains "subject" "Receipt")
{
  # Tithe
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "Myaccount@spectrumemails.com", header :contains "subject" "Thanks for your payment")
{
  # Spectrum
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "discover@services.discover.com", header :contains "subject" "Your Scheduled Payment")
{
  # Discover
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "no-reply@alertsp.chase.com", header :contains "subject" "Thank you for scheduling your credit card payment")
{
  # Chase
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "venmo@venmo.com", header :contains "subject" "paid")
{
  # Venmo
  fileinto "Receipts";
  fileinto "Finance";

  # Enabling this for EVA because it's how I often pay contractors.
  set "eva" "true";
}
elsif address :is "from" "admin@indyvineyard.org"
{
  # Tithe: Indy Vinyard
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif address :is "from" "no-reply@churchcenter.com"
{
  # Tithe: Thrive
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif header :contains "subject" "You submitted an order in the amount of"
{
  # Paypal
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "centerpoint_energy@tmr3.com", header :contains "subject" "bill is available to view online")
{
  # Centerpoint
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "info@mohela.com", header :contains "subject" "Your MOHELA Payment")
{
  # Mohela
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif allof (address :is "from" "noreply@myloanweb.com")
{
  # BSI Mortgage
  fileinto "Finance";
  # Don't folder this one.
  set "eva" "false";
}
elsif allof (address :is "from" "DukeEnergyPaperlessBilling@paperless.dukeenergy.com", header :contains "subject" "statement")
{
  # Duke Energy
  fileinto "Finance";
  fileinto "Receipts";
  set "eva" "false";
}
elsif allof (address :is "from" "emailreply@csaa.com", header :contains "subject" "Your Automatic Payment is scheduled")
{
  # Triple AAA
  fileinto "Finance";
  fileinto "Receipts";
  set "eva" "false";
}
elsif allof (address :is "from" "no-reply@invoicecloud.net", header :contains "subject" "Payment Confirmation")
{
  # Invoice Cloud, Carmel Utilities
  fileinto "Finance";

  if anyof (header :contains "subject" "Payment Confirmation")
  {
    fileinto "Receipts";
  } else
  {
    fileinto "Notification";
    expire "day" "3";
  }

  set "eva" "false";
}
elsif allof (address :is "from" "Billing_Web@QuestDiagnostics.com", header :contains "subject" "Your Payment Submitted")
{
  # Quest Diagnostics
  fileinto "Finance";
  fileinto "Receipts";
  set "eva" "false";
}
elsif allof (address :is "from" "Receipts@united.com")
{
  # United Airlines
  fileinto "Finance";
  fileinto "Receipts";
  set "eva" "true";
}
elsif allof (address :is "from" "steve.boles@missiontoukraine.org", header :contains "subject" "Donation Receipt")
{
  # Mission to Ukraine
  fileinto "Finance";
  fileinto "Receipts";
  set "eva" "false";
}
elsif allof (address :is "from" "service@paypal.com", header :contains "subject" "Receipt")
{
  fileinto "Receipts";
  fileinto "Finance";
  set "eva" "false";
}
elsif anyof (header :contains "subject" "order confirmed")
{
  # AliExpress
  fileinto "Receipts";
  set "eva" "true";
}
elsif allof (address :is "from" "noreply@steampowered.com", header :contains "subject" "Thank you for your Steam purchase!")
{
  fileinto "Receipts";
  set "eva" "false";
}
elsif allof (address :domain "from" "messaging.squareup.com", header :contains "subject" "Receipt")
{
  # Square vendors
  fileinto "Receipts";
}
elsif allof (address :domain "from" "glossgenius.com", header :contains "subject" "receipt")
{
  # Gloss vendors (like barbers)
  fileinto "Receipts";
}


#####################################
# Notifications, News, and Expiring #
#####################################

if allof (address :domain "from" "amazon.com")
{
  # Amazon
  fileinto "Notification";
  expire "day" "3";
  set "eva" "true";
}
elsif anyof (address :domain "from" "notice.aliexpress.com")
{
  # AliExpress
  fileinto "Notification";
  expire "day" "3";
  set "eva" "true";
}
elsif allof (address :is "from" "dailybriefing@thomsonreuters.com")
{
  # Reuters
  fileinto "News";
  fileinto "Newsletters";
  set "eva" "false";
}
elsif allof (address :domain "from" "reason.com")
{
  # Reason
  fileinto "News";
  fileinto "Newsletters";
  set "eva" "false";
}
elsif allof (address :domain "from" "nomadcapitalist.com")
{
  # Nomad Capitalist
  fileinto "News";
  fileinto "Newsletters";
  set "eva" "false";
}
elsif anyof
  (
    header :contains "subject" "Sign-in attempt",
    header :contains "subject" "device added",
    header :contains "subject" "Verification Code",
    header :contains "subject" "sign in",
    header :contains "subject" "Verify Your",
    header :contains "subject" "Verify your email address"
  )
{
  # Security
  fileinto "Notification";
  expire "day" "1";
  set "eva" "false";
}
elsif allof (address :is "from" "appointmentreminders@therapyportal.com", header :contains "subject" "Appointment Reminder") {
  # Appointment reminders
  fileinto "Notification";
  expire "day" "7";
  set "eva" "true";
}
elsif allof (address :domain "from" "attestation.app", header :contains "subject" "failed to provide valid attestations")
{
  # Graphene Attestation App
  fileinto "Notification";
  expire "day" "1";
  set "eva" "false";
}
elsif address :contains "from" "kusterchronicle" {
  # Kuster Chronicle
  fileinto "News";
  fileinto "Newsletters";
  set "eva" "false";
}
elsif anyof (header :contains "subject" "new device")
{
  # New device logins
  fileinto "Notification";
  expire "day" "3";
  set "eva" "false";
}
# steam sale
elsif allof (address :domain "from" "steampowered.com", header :contains "subject" "on sale")
{
  fileinto "Notification";
  expire "day" "7";
  set "eva" "false";
}
# tim ferriss "max.ocull+tim.ferriss@protonmail.com"
# empower weekly report: "charges this week."
elsif anyof (address :is "to" "max.ocull+tim.ferriss@protonmail.com")
{
  # Tim Ferriss
  fileinto "News";
  fileinto "Newsletters";
  set "eva" "false";
}
elsif anyof (header :contains "subject" "charges this week.")
{
  # Empower Weekly Report
  fileinto "News";
  fileinto "Finance";
  expire "day" "3";
}
elsif anyof (address :is "from" "maxocull.com@gmail.com")
{
  # Home Lab
  fileinto "Notification";
  fileinto "Software";
  expire "day" "1";
  set "eva" "false";
}
elsif anyof (address :is "from" "lwn@lwn.net")
{
  # LWN
  fileinto "News";
  fileinto "Newsletters";
  set "eva" "false";
}
elsif anyof (address :is "from" "noreply@camelcamelcamel.com")
{
  # Camel Camel Camel
  fileinto "Notification";
  expire "day" "1";

  # Let EVA know about this so we can snatch it up.
  set "eva" "true";
}
elsif anyof (address :domain "from" "lists.archlinux.org")
{
  # Arch Security
  fileinto "News";
  fileinto "Software";
  fileinto "Newsletters";
  set "eva" "false";
}
elsif anyof (address :domain "from" "linkedin.com")
{
  # LinkedIn
  fileinto "Social";
  fileinto "Notification";
  expire "day" "3";
}
elsif anyof (header :contains "subject" "wishlist")
{
  # Sale on a wishlisted item anywhere.
  fileinto "Urgent";
  expire "day" "7";
}

########
# Work #
########

# If the email is from Hilton, Lyft, or United, forward it to my work email.
if anyof (
  address :domain "from" "hilton.com",
  address :domain "from" "lyft.com",
  address :domain "from" "united.com"
) {
  fileinto "Special";
  set "eva" "true";
  # redirect "mocull@auranetworksystems.com";
  # redirect "paulagil@proton.me";
}

##########
# Upwork #
##########

if anyof (
    address :domain "from" "upwork.com",
    address :domain "from" "upworkmail.com"
  )
{
  fileinto "Notification";
  fileinto "Finance";
  set "eva" "false";

  if anyof(
      header :contains "subject" "time was added"
    )
  {
    expire "day" "1";
  }
}

####################
# Exclude from EVA #
####################

if anyof (
    address :domain "from" "upwork.com"
  )
{
  fileinto "Finance";
  set "eva" "false";
}

####################
# Forward to EVA #
####################

if anyof(
    string :is "${eva}" "unset",
    string :is "${eva}" "true"
  )
{
  fileinto "EVA";
  # redirect :copy "paulagil@proton.me";
}
