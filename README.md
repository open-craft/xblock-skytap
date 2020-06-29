# xblock-skytap

## What is it?

An XBlock for integrating [Open edX](https://open.edx.org/) and [Skytap](https://www.skytap.com/).

## Support

| Open edX Release | Tag |
|:-----------------|:---:|
| Juniper | v0.2 |
| Ironwood | v0.1 |

## Install 

See [edX Installing an XBlock](http://edx.readthedocs.io/projects/edx-installing-configuring-and-running/en/latest/configuration/install_xblock.html?highlight=install%20xblock)
for details on how to install this XBlock on your Open edX instance.

```python
pip install "git+https://github.com/open-craft/xblock-skytap@master#egg=xblock-skytap"
```

## Testing

The test suite uses `tox`, so install it into a virtualenv to run the tests:

```bash
pip install tox
```

Accordingly, all you need to do in the repo's directory is to run the following:

```bash
tox
```

## Installing on DevStack

1. Start your *edX devstack*
2. Once the *edX devstack* is up, run `make studio-shell`
3. `source ../venvs/edxapp/bin/activate`
4. `sudo -u edxapp /edx/bin/pip.edxapp install "git+https://github.com/open-craft/xblock-skytap@master#egg=xblock-skytap"`
5. `docker-compose restart studio`
6. Repeat steps 2 till 5 using `lms` instead of `studio`, ei. `make lms-shell` and `docker-compose restart lms`.
