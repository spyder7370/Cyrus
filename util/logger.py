import logging as log


log.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(filename)s:%(lineno)d: %(message)s",
    style="%",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=log.INFO,
)
