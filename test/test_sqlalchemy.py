from model import ProxyModel
from manager import ProxyManager

if __name__ == '__main__':
    # Config.Base.metadata.drop_all(Config.engine)
    # Config.Base.metadata.create_all(Config.engine)
    pm = ProxyManager()
    pm.add_proxy(ProxyModel.from_url('http://27.208.25.190:8060'))
