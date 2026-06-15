import mongoengine as me


def connect_db(host=None):
    """Connect to MongoDB. Called during app initialization."""
    if host:
        me.connect(host=host)
    else:
        me.connect()
