import redis, json

class Service ():
    
    def __init__(self, service_id):
        # obtain identity
        self.service_id = service_id
        
        # setup redis connection
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.p = self.r.pubsub()
        
        # obtain state from redis or create new state
        state = self.r.get('service:{0}:state'.format(self.service_id));
        try:
            self.state = json.loads(state)
        except:
            self.state = {'subscribed_to':[]}
        print self.state
        
        # subscribe to any channels
        for c in self.state['subscribed_to']:
            self.p.subscribe(c)
                    
        # do any service-type specific initialization
        try:
            self.init()
        except:
            pass

    # function used to subscribe a service to another service
    def subscribe(self, input_service_id):
        channel = 'service:{0}:channel'.format(input_service_id)
        self.state['subscribed_to'].append(channel)
        self.p.subscribe(channel)
    
    
    def run (self):
        # start running the service, wait for any output from services subscribed to
        for m in self.p.listen():
            if m['type'] == 'message':
                self.execute({'c':m['channel'], 'd':m['data']})
                self.persist_service()
    
    # saves current state of service to redis            
    def persist_service (self):
        self.r.set('service:{0}:state'.format(self.service_id), json.dumps(self.state))
        
    # saves some output of service to database
    def persist_output (self, m):
        pass
        
    # publish output to subscribed services
    def publish_output (self, m):
        self.r.publish('service:{0}:channel'.format(self.service_id), m)
        
	def publish_stderr (self, m):
        self.r.publish('service:{0}:stderr'.format(self.service_id), m)
        
class CounterService (Service):
    
    def init (self):
        self.state['data'] = 0
        
    def execute (self, m):
        self.state['data'] += 1
        print self.state['data']
        self.publish_output(self.state['data'])
        
class IntegratorService (Service):
    
    def init (self):
        self.state['data'] = 0
    
    def execute (self, m):
        try:
            d = int(m['d'])
        except:
            d = 0
        self.state['data'] += d
        print self.state['data']
        self.publish_output(self.state['data'])
        
    
class DifferentiatorService (Service):
    
    def init (self):
        self.state['prev'] = 0
    
    def execute (self, m):
        try:
            d = int(m['d'])
            print(d - self.state['prev'])
            self.publish_output(d - self.state['prev'])
            self.state['prev'] = d    
        except:
            pass
        
        
