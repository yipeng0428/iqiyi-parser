

import threading


class Allotter(object):

    def __init__(self, Handler, GlobalProgress):
        self.globalprog = GlobalProgress
        self.handler = Handler

        self.__allotter_lock__ = threading.Lock()

    def makeBaseConn(self):

        ranges = self.blockToRange(self.makeEvenBlock(len(self.handler.url.getUrls())))

        for i, j in enumerate(self.handler.url.getUrls().keys()):
            self.globalprog.insert(j, *ranges[i])


    def splitRange(self, Range, num):
        each = int((Range[1] - Range[0]) / num)

        retlist = []

        for i in range(num):
            retlist.append((Range[0] + each * i, Range[0] + each * (i+1)))

        if Range[1] > retlist[-1][1]:
            retlist[-1] = (retlist[-1][0], Range[1])

        return retlist

    def makeEvenBlock(self, block_num):
        if not self.globalprog.block_map:
            self.globalprog.makeMap()

        each_block = int(len(self.globalprog.getMap()) / block_num)

        blocks = []

        for i in range(block_num):
            blocks.append((i * each_block, (i+1) * each_block))

        blocks[-1] = (blocks[-1][0], len(self.globalprog.getMap()))

        # ranges = self.blockToRange(blocks)

        return blocks

        # for i, j in enumerate(self.handler.url.getUrls().keys()):
        #     self.globalprog.insert(j, *ranges[i])

    def assignAll(self):
        ranges = self.blockToRange(self.makeEvenBlock(self.handler.url.max_conn))

        for i in range(self.handler.url.max_conn):
            self.globalprog.insert(i, )


    def getUrlsThread(self):
        url_thread_table = [[] for i in range(len(self.handler.url.id_map))]

        for i in self.globalprog.progresses.values():
            if not i.isGoEnd():
                url_thread_table[i.urlid].append(i)

        return url_thread_table

    def getIdleUrl(self):
        idle_url = []
        url_health = self.getUrlsHealth()
        for i in self.handler.url.getUrls().keys():
            for m in url_health:
                if m[0] == i:
                    break
            else:
                idle_url.append(i)

        return idle_url

    def assignUrl(self):
        url_health_table = self.getUrlsHealth()
        url_thread_table = self.getUrlsThread()

        idle_url = self.getIdleUrl()

        if not idle_url:
            while True:
                if not url_health_table:
                    put_urlid = -1
                    break
                put_urlid = url_health_table.pop(-1)[0]

                if self.handler.url.dict[put_urlid].max_thread == -1 or \
                        len(url_thread_table[put_urlid]) < self.handler.url.dict[put_urlid].max_thread:
                    break

        else:
            put_urlid = idle_url[0]

        return put_urlid


    def assignRange(self):
        free_blocks = self.getFreeBlock()

        half_block = [(int((i[1] - i[0]) / 2) + i[0], i[1]) for i in free_blocks]

        ranges_table = self.blockToRange(half_block)

        put_range = ranges_table[-1] if ranges_table else []

        return put_range

    def assign(self):
        return self.assignUrl(), self.assignRange()

    def getUrlsHealth(self):
        """return: [(Urlid, AvgSpeed), ...]"""

        urlspeed = {}

        for i in self.globalprog.progresses.values():
            if not i.isEnd():
                urlspeed[i.urlid] = (urlspeed.get(i.urlid, (0, 0))[0]+1,
                                     urlspeed.get(i.urlid, (0, 0))[1] + i.getAvgSpeed())

        for i, j in urlspeed.items():
            urlspeed[i] = j[1] / j[0]

        speed_table = sorted(urlspeed.items(), key=lambda x: x[1])


        return speed_table


    def getFreeBlock(self):

        free_list = []

        block_head = None

        tmp_map = self.globalprog.getMap()

        for i, j in enumerate(tmp_map):
            if j is None:
                if block_head is None:
                    block_head = i
            else:
                if block_head is not None:
                    free_list.append((block_head, i))
                    block_head = None

        if block_head is not None:
            free_list.append((block_head, len(tmp_map)-1))

        return sorted(free_list, key=lambda x: (x[1] - x[0]))

    def blockToRange(self, block_list):
        retranges = []
        for i in block_list:
            retranges.append((i[0] * self.handler.file.BLOCK_SIZE,
                              i[1] * self.handler.file.BLOCK_SIZE))

        if retranges and retranges[-1][1] + self.handler.file.BLOCK_SIZE > self.handler.file.size:
            retranges[-1] = (retranges[-1][0], self.handler.file.size)

        return retranges




