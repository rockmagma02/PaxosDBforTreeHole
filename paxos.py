import collections
import threading

ProposalID = collections.namedtuple('ProposalID', ['number', 'uid'])


class Messenger (object):
    def send_prepare(self, proposal_id):
        '''
        Broadcasts a Prepare message to all Acceptors
        '''

    def send_promise(self, proposer_uid, proposal_id, previous_id, accepted_value):
        '''
        Sends a Promise message to the specified Proposer
        '''

    def send_accept(self, proposal_id, proposal_value):
        '''
        Broadcasts an Accept message to all Acceptors
        '''

    def send_accepted(self, proposal_id, accepted_value):
        '''
        Broadcasts an Accepted message to all Learners
        '''

    def on_resolution(self, proposal_id, value):
        '''
        Called when a resolution is reached
        '''


    
class Proposer (object):

    def __init__(self, messenger, uid, quorum_size) -> None:
        self.messenger            = messenger
        self.proposer_uid         = uid
        self.quorum_size          = quorum_size
        self.mutex                = threading.Lock()

        self.proposed_value       = None
        self.proposal_id          = None 
        self.last_accepted_id     = None
        self.next_proposal_number = 1
        self.promises_rcvd        = None

    
    def set_proposal(self, value):
        '''
        Sets the proposal value for this node. 
        '''
        self.mutex.acquire()
        if self.proposed_value is None:
            self.proposed_value = value
        self.mutex.release()


    def prepare(self):
        '''
        Sends a prepare request to all Acceptors.
        '''
        self.mutex.acquire()        
        self.promises_rcvd = set()
        self.proposal_id   = ProposalID(self.next_proposal_number, self.proposer_uid)
        self.next_proposal_number += 1
        self.mutex.release()
        self.messenger.send_prepare(self.proposal_id)

    
    def recv_promise(self, from_uid, proposal_id, prev_accepted_id, prev_accepted_value):
        '''
        Recieve a Promise message from an Acceptor.
        '''
        self.mutex.acquire()
        if proposal_id != self.proposal_id or from_uid in self.promises_rcvd:
            return

        self.promises_rcvd.add( from_uid )
        
        if prev_accepted_id > self.last_accepted_id:
            self.last_accepted_id = prev_accepted_id
            if prev_accepted_value is not None:
                self.proposed_value = prev_accepted_value

        if len(self.promises_rcvd) == self.quorum_size:
            
            if self.proposed_value is not None:
                self.messenger.send_accept(self.proposal_id, self.proposed_value)
        self.mutex.release()


        
class Acceptor (object):

    def __init__(self, messenger) -> None:
        self.messenger      = messenger
        self.promised_id    = None
        self.accepted_id    = None
        self.accepted_value = None
        self.mutex          = threading.Lock()


    def recv_prepare(self, from_uid, proposal_id):
        '''
        Answer Prepare from Proposer
        '''
        self.mutex.acquire()
        if proposal_id == self.promised_id:
            self.messenger.send_promise(from_uid, proposal_id, self.accepted_id, self.accepted_value)
        
        elif proposal_id > self.promised_id:
            self.promised_id = proposal_id
            self.messenger.send_promise(from_uid, proposal_id, self.accepted_id, self.accepted_value)
        self.mutex.release()

                    
    def recv_accept_request(self, proposal_id, value):
        '''
        Answer Accept from Proposer
        '''
        self.mutex.acquire()
        if proposal_id >= self.promised_id:
            self.promised_id     = proposal_id
            self.accepted_id     = proposal_id
            self.accepted_value  = value
            self.messenger.send_accepted(proposal_id, self.accepted_value)
        self.mutex.release()


    
class Learner (object):

    def __init__(self,quorum_size) -> None:
        self.quorum_size       = quorum_size
        self.mutex          = threading.Lock()

        self.proposals         = None 
        self.acceptors         = None 
        self.final_value       = None
        self.final_proposal_id = None

    def complete(self):
        return self.final_proposal_id is not None

    def recv_accepted(self, from_uid, proposal_id, accepted_value):
        '''
        Receive Accepted message from Acceptor
        '''

        if self.final_value is not None:
            return
        self.mutex.acquire()
        if self.proposals is None:
            self.proposals = dict()
            self.acceptors = dict()
        
        last_pn = self.acceptors.get(from_uid)

        if not proposal_id > last_pn:
            return

        self.acceptors[ from_uid ] = proposal_id
        
        if last_pn is not None:
            oldp = self.proposals[ last_pn ]
            oldp[1] -= 1
            if oldp[1] == 0:
                del self.proposals[ last_pn ]

        if not proposal_id in self.proposals:
            self.proposals[ proposal_id ] = [0, 0, accepted_value]

        t = self.proposals[ proposal_id ]

        t[0] += 1
        t[1] += 1

        if t[0] == self.quorum_size:
            self.final_value       = accepted_value
            self.final_proposal_id = proposal_id
            self.proposals         = None
            self.acceptors         = None

            self.messenger.on_resolution(proposal_id, accepted_value)
        self.mutex.release()