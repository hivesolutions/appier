workflow "Build and Test" {
  on = "push"
  resolves = [
    "Master",
  ]
}

action "Build" {
  uses = "hivesolutions/@master"
  args = "pip install -r requirements.txt && pip install -r extra.txt"
}

action "Test" {
  uses = "jefftriplett/python-actions@master"
  args = "python setup.py test"
  needs = ["Build"]
}

action "Master" {
  uses = "actions/bin/filter@master"
  needs = [
    "Test"
  ]
  args = "branch master"
}
