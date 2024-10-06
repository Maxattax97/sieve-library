require ["fileinto"];

if allof (address :domain "from" "github.com")
{
  # Github
  fileinto "Software";
}
