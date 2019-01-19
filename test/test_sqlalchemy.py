from manager import ProxyManager
from model import ProxyModel

if __name__ == '__main__':
    # Config.Base.metadata.drop_all(Config.engine)
    # Config.Base.metadata.create_all(Config.engine)
    pm = ProxyManager()
    pm.add_proxy(ProxyModel.instance('http://27.208.25.190:8060'))
