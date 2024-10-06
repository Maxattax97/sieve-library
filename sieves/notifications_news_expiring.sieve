require ["fileinto", "imap4flags", "vnd.proton.expire"];

if allof (address :domain "from" "amazon.com")
{
  # Amazon
  fileinto "Notification";
  expire "day" "7";
}
elsif allof (address :is "from" "dailybriefing@thomsonreuters.com")
{
  # Reuters
  fileinto "News";
  expire "day" "5";
}
elsif anyof (header :contains "subject" "Sign-in attempt", header :contains "subject" "device added", header :contains "subject" "Verification Code", header :contains "subject" "sign in")
{
  # Security
  fileinto "Notification";
  expire "day" "3";
}
elsif allof (address :is "from" "appointmentreminders@therapyportal.com", header :contains "subject" "Appointment Reminder") {
  # Appointment reminders
  fileinto "Notification";
  expire "day" "7";
}
