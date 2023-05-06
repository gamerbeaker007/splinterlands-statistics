from urllib3 import Retry


class LogRetry(Retry):
    """
     Adding extra logs before making a retry request
    """
    def __init__(self, *args, **kwargs):
        print("Retry... api call backoff/wait sequence 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s")
        super().__init__(*args, **kwargs)
