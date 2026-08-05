# Append to the DOJO's test/conftest.py, and add `import os` at the top if it
# is not already there.
#
# The repository is taken from the environment so a fork can be tested without
# editing the file: CAR_HACKING_DOJO_REPO=<account>/car-hacking-dojo

@pytest.fixture(scope="session")
def car_hacking_dojo(admin_session):
    repository = os.getenv("CAR_HACKING_DOJO_REPO", "studycrack/car-hacking-dojo")
    try:
        rid = create_dojo(repository, session=admin_session)
    except AssertionError:
        rid = "car-hacking"
    try:
        make_dojo_official(rid, admin_session)
    except AssertionError:
        pytest.skip(f"car-hacking dojo unavailable; set CAR_HACKING_DOJO_REPO (tried {repository})")
    return rid
