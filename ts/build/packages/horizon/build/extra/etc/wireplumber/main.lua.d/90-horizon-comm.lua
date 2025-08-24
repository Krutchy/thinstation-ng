-- Treat VMware Horizon as a communications app
rule = {
  matches = {
    { { "application.process.binary", "equals", "horizon-client" } },
    { { "application.name", "matches", "Omnissa Horizon Client*" } },
  },
  apply_properties = {
    ["media.role"] = "Communication",
  }
}

table.insert(policy.rules, rule)
