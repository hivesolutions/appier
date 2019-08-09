workflow "Build and Test" {
  on = "push"
  resolves = [
    "Master",
  ]
}

action "Build" {
  uses = "jefftriplett/python-actions@master"
  args = "pip install -r requirements.txt"
}

action "Test" {
  uses = "jefftriplett/python-actions@master"
  args = "pytest"
  needs = ["Build"]
}

action "Master" {
  uses = "actions/bin/filter@master"
  needs = [
    "Test",
  ]
  args = "branch master"
}
