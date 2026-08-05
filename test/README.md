# Tests

`test_car_hacking.py` covers every challenge in this dojo: it starts each one
in a real workspace, solves it the way a student would, and submits the flag
through the API. Several tests also assert the *mechanism* rather than only the
outcome --- that a passive scan cannot see the scan response, that an
unconfirmed indication stops after one record, that rewriting a single
controller's mileage is detected --- so that a challenge cannot quietly become
easier than it was written to be.

## Running them

These are DOJO tests and need the DOJO's own fixtures, so they run from a
checkout of [pwncollege/dojo](https://github.com/pwncollege/dojo) rather than
from here:

```bash
cp test/test_car_hacking.py       <dojo-checkout>/test/
cat test/conftest-fixture.py   >> <dojo-checkout>/test/conftest.py   # once
```

Then, with the platform running:

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock -v $PWD:/opt/pwn.college \
  -e DOJO_CONTAINER=dojo -e CAR_HACKING_DOJO_REPO=<account>/car-hacking-dojo \
  dojo-test pytest -v /opt/pwn.college/test/test_car_hacking.py
```

`test_dbc` needs `cantools`, which arrives with challenge image `v3`. A dojo
still pointing at an older image will fail that one, correctly.

## What is not covered

The tests exercise the challenges. They do not exercise the emulation's
fidelity claims --- that the ATT PDUs match the specification, or that the CAN
shim behaves as a kernel socket would. Those are argued in the READMEs and
checked by hand.
