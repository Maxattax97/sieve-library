require ["fileinto", "imap4flags", "vnd.proton.expire", "variables"];
# require ["redirect"];

set "eva" "unset";

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
elsif anyof (header :contains "subject" "Privacy Policy")
{
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
    address :is "from" "glsamaker@gentoo.com"
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
    address :domain "from" "duke-energyalert.com",
    address :contains "from" "huntington",
    address :domain "from" "venmo.com",
    allof (address :is "from" "service@sfmc.personalwealth.empower.com", header :contains "subject" "Your daily financial monitor")
) {
  fileinto "Finance";
  set "eva" "false";

  if anyof (
      header :contains "subject" "Your Monthly Statement is Available",
      header :contains "subject" "Review your recent activity",
      header :contains "subject" "Thank you for your payment",
      header :contains "subject" "Payment confirmation",
      header :contains "subject" "transaction history",
      header :contains "subject" "Funds invested"
  ) {
      fileinto "Trash";
  }

  if anyof (
      header :contains "subject" "Scheduled transfer created",
      header :contains "subject" "IBKR FYI"
  ) {
    expire "day" "3";
  }
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

#####################
# Growth #
#####################

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
    header :contains "subject" "Requests Your Feedback"
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
  set "eva" "false";
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
  fileinto "Receipts";
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

#####################################
# Notifications, News, and Expiring #
#####################################

if allof (address :domain "from" "amazon.com")
{
  # Amazon
  fileinto "Notification";
  expire "day" "7";
  set "eva" "true";
}
elsif allof (address :is "from" "dailybriefing@thomsonreuters.com")
{
  # Reuters
  fileinto "News";
  expire "day" "5";
  set "eva" "false";
}
elsif allof (address :domain "from" "nomadcapitalist.com")
{
  # Nomad Capitalist
  fileinto "News";
  expire "day" "5";
  set "eva" "false";
}
elsif anyof (header :contains "subject" "Sign-in attempt", header :contains "subject" "device added", header :contains "subject" "Verification Code", header :contains "subject" "sign in")
{
  # Security
  fileinto "Notification";
  expire "day" "3";
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
elsif address :is "from" "kusterchronicle@send.mailchimpapp.com" {
  # Kuster Chronicle
  fileinto "News";
  expire "day" "7";
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
