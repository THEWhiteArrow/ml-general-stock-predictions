import injector
from gsp.mongodb.storage_helper_protocol import StorageHelperProtocol
from gsp.mongodb.storage_helper import StorageHelper


def create_container():
    container = injector.Injector()
    container.binder.bind(StorageHelperProtocol, to=StorageHelper)

    return container


container = create_container()
