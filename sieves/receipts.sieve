require ["fileinto", "imap4flags"];

# I used to do this but I stopped.
# addflag "\\Seen";

if allof (address :domain "from" "ting.com", header :contains "subject" "bill has been paid")
{
  # Ting
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "info@myiclubonline.com", header :contains "subject" "Your online payment receipt")
{
  # Planet Fitness
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :domain "from" "pushpay.com", header :contains "subject" "Receipt")
{
  # Tithe
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "Myaccount@spectrumemails.com", header :contains "subject" "Thanks for your payment")
{
  # Spectrum
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "discover@services.discover.com", header :contains "subject" "Your Scheduled Payment")
{
  # Discover
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "no-reply@alertsp.chase.com", header :contains "subject" "Thank you for scheduling your credit card payment")
{
  # Chase
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "venmo@venmo.com", header :contains "subject" "You paid")
{
  # Venmo
  fileinto "Receipts";
  fileinto "Finance";
}
elsif address :is "from" "admin@indyvineyard.org"
{
  # Tithe: Indy Vinyard
  fileinto "Receipts";
  fileinto "Finance";
}
elsif address :is "from" "no-reply@churchcenter.com"
{
  # Tithe: Thrive
  fileinto "Receipts";
  fileinto "Finance";
}
elsif header :contains "subject" "You submitted an order in the amount of"
{
  # Paypal
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "centerpoint_energy@tmr3.com", header :contains "subject" "bill is available to view online")
{
  # Centerpoint
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "info@mohela.com", header :contains "subject" "Your MOHELA Payment")
{
  # Mohela
  fileinto "Receipts";
  fileinto "Finance";
}
elsif allof (address :is "from" "noreply@myloanweb.com")
{
  # BSI Mortgage
  fileinto "Finance";
  # Don't folder this one.
}
elsif allof (address :is "from" "DukeEnergyPaperlessBilling@paperless.dukeenergy.com", header :contains "subject" "statement")
{
  # Duke Energy
  fileinto "Finance";
  fileinto "Receipts";
}
elsif allof (address :is "from" "emailreply@csaa.com", header :contains "subject" "Your Automatic Payment is scheduled")
{
  # Triple AAA
  fileinto "Finance";
  fileinto "Receipts";
}
