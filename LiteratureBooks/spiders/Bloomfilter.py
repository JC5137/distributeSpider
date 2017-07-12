# encoding=utf-8
# reference: http://blog.csdn.net/bone_ace/article/details/53107018
from hashlib import md5
from MyRedis import get_redis


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed
    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret

class BloomFilter(object):
    def __init__(self, blockNum= 1, key='bloomfilter'):
        """
        :param host: the host of Redis
        :param port: the port of Redis
        :param db: witch db in Redis
        :param key: the key's name in Redis
        """
        self.server = get_redis()
        self.bit_size = 1 << 16  #Redis的String类型最大容量为512M，现使用8K
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.key = key
        self.blockNum = blockNum
        self.hashfunc = []
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))
    
    def is_contains(self, str_input):
        if not str_input:
            return False
        str_input = self._get_str_md5(str_input)
        is_contain = True
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            is_contain = is_contain & self.server.getbit(name, loc)
        return is_contain

    def insert(self, str_input):
        str_input = self._get_str_md5(str_input)
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)
    #获取str_input的md5编码
    def _get_str_md5(self, str_input):
        return md5(str_input).hexdigest()

if __name__ == '__main__':
    # 第一次运行时会显示 not exists!，之后再运行会显示 exists!
    bf = BloomFilter()
    str = '//item.jd.com/11291428.html' + '￥18.3'
    if bf.is_contains(str):   # 判断字符串是否存在
        print 'exists!'
    else:
        print 'not exists!'
        bf.insert('http://www.baidu.com')
