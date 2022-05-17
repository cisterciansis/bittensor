import bittensor
import torch
from typing import Union, List, Tuple, Optional

from bittensor._serializer import serializer
from .synapse_impl import Synapse

class TextSeq2Seq (Synapse):
    """ TextSeq2Seq Synapse type for sequence generation from language models.
    """
    synapse_type: bittensor.proto.Synapse.SynapseType = bittensor.proto.Synapse.SynapseType.TEXT_SEQ_2_SEQ
    def __init__( 
        self, 
        topk:int = 512, 
        num_to_generate: int = 512,
        forward_request_serializer_type: 'bittensor.proto.Serializer.Type' = bittensor.proto.Serializer.MSGPACK,
        forward_response_serializer_type: 'bittensor.proto.Serializer.Type' = bittensor.proto.Serializer.MSGPACK,
        backward_request_serializer_type: 'bittensor.proto.Serializer.Type' = bittensor.proto.Serializer.MSGPACK,
        backward_response_serializer_type: 'bittensor.proto.Serializer.Type' = bittensor.proto.Serializer.MSGPACK,
    ) -> 'TextSeq2Seq':  
        """ TextSeq2Seq Synapse initializer.
        Args:
            Topk (:obj:int, :default: 512):
                The top k number of logits to compress and send over the wire 
            num_to_generate (:obj: int, :default: 512):
                The number of tokens to generate using the language model
            forward_request_serializer_type (:obj:`bittensor.proto.Serializer.Type` of shape :obj:`(1)`, `optional`, :default: `bittensor.proto.Serializer.MSGPACK`):
                Serializer used to pack torch tensors on forward request.
            forward_response_serializer_type (:obj:`bittensor.proto.Serializer.Type` of shape :obj:`(1)`, `optional`, :default: `bittensor.proto.Serializer.MSGPACK`):
                Serializer used to pack torch tensors on forward response.
            backward_request_serializer_type (:obj:`bittensor.proto.Serializer.Type` of shape :obj:`(1)`, `optional`, :default: `bittensor.proto.Serializer.MSGPACK`):
                Serializer used to pack torch tensors on forward request.
            backward_response_serializer_type (:obj:`bittensor.proto.Serializer.Type` of shape :obj:`(1)`, `optional`, :default: `bittensor.proto.Serializer.MSGPACK`):
                Serialzer used to pack torch tensors on backward response.
        Returns:
            TextLastHiddenState (:obj:`TextLastHiddenState`, `required`):
                TextLastHiddenState instance adapter class.
    """
        super().__init__ (
            forward_request_serializer_type,
            forward_response_serializer_type,
            backward_request_serializer_type,
            backward_response_serializer_type
        )
        self.topk = topk
        self.num_to_generate = num_to_generate
        self.synapse_type = TextSeq2Seq.synapse_type

    def __repr__(self) -> str: return self.__str__()
    def __str__(self) -> str: return "TextSeq2Seq"

    @staticmethod
    def deserialize_from_instance_proto ( instance_proto: bittensor.proto.Synapse ) -> 'Synapse':
        """ Deserialzied the instance proto to an instance class."""
        return TextSeq2Seq (
            topk = instance_proto.topk,
            num_to_generate = instance_proto.num_to_generate,
            forward_request_serializer_type = instance_proto.forward_request_serializer_type,
            forward_response_serializer_type = instance_proto.forward_response_serializer_type,
            backward_request_serializer_type = instance_proto.backward_request_serializer_type,
            backward_response_serializer_type = instance_proto.backward_response_serializer_type,
        )

    @staticmethod
    def deserialize_from_wire_proto ( wire_proto: bittensor.proto.Synapse ) -> 'Synapse':
        """ Deserialzied the wire proto to an instance class. """
        instance_proto = bittensor.proto.Synapse.TextSeq2Seq()
        instance_proto.ParseFromString( wire_proto.synapse_data )
        return TextSeq2Seq.deserialize_from_instance_proto( instance_proto )

    def serialize_to_instance_proto( self ) -> 'bittensor.proto.Synapse.TextSeq2Seq':
        """ Serializes the class instance to a Synapse instance proto."""
        return bittensor.proto.Synapse.TextSeq2Seq ( 
            topk = self.topk, 
            num_to_generate = self.num_to_generate,
            forward_request_serializer_type = self.forward_request_serializer_type,
            forward_response_serializer_type = self.forward_response_serializer_type,
            backward_request_serializer_type = self.backward_request_serializer_type,
            backward_response_serializer_type = self.backward_response_serializer_type,
        )

    def serialize_to_wire_proto( self, code: 'bittensor.proto.ReturnCode' = 0, message: str = ''  ) -> bittensor.proto.Synapse:
        """ Serializes the class instance to a Synapse wire proto. """
        return bittensor.proto.Synapse (
                synapse_data = self.serialize_to_instance_proto().SerializeToString(),
                synapse_type = TextSeq2Seq.synapse_type,
                return_code = code,
                message = message
            )

    def check_forward_request_tensor     ( self, forward_request_tensor ):
        if len( forward_request_tensor.shape ) != 2:
            raise ValueError( "forward_request_tensor.shape must be in [-1, -1], got: {} for synapse: {}".format( list(forward_request_tensor.shape), self ) ) 

    def check_forward_response_tensor    ( self, forward_request_tensor, forward_response_tensor ):
        if ( len( forward_response_tensor.shape ) != 2 or
             forward_response_tensor.size(0) != forward_request_tensor.size(0) or
             forward_response_tensor.size(1) > self.num_to_generate 
            ):
            raise ValueError( "forward_response_tensor.shape must be in [{}, {}], got: {} for synapse: {}".format( forward_request_tensor.size(0) , self.num_to_generate, list(forward_response_tensor.shape), self ) ) 

    def check_backward_request_gradient  ( self, forward_request_tensor, backward_request_gradient ):
        if list( backward_request_gradient.shape ) != list( forward_request_tensor.shape ):
            raise ValueError( "backward_request_gradient.shape: {} must be equivalent to forward_request_tensor.shape: {} for synapse: {}".format( list( backward_request_gradient.shape ), list(forward_request_tensor.shape), self ) ) 

    def encode_forward_request_tensor    ( self, forward_request_tensor: torch.Tensor ) -> torch.Tensor: 
        return forward_request_tensor
        
    def decode_forward_request_tensor    ( self, forward_request_tensor: torch.Tensor ) -> torch.Tensor: 
        return forward_request_tensor

    def encode_forward_response_tensor   ( self, forward_response_tensor: torch.Tensor ) -> torch.Tensor: 
        # Apply topk logit encoding.
        return forward_response_tensor

    def decode_forward_response_tensor   ( self, forward_response_tensor: torch.Tensor ) -> torch.Tensor: 
        # Decode topk logit encoding.
        return forward_response_tensor

    def encode_backward_request_gradient ( self, backward_request_gradient: torch.Tensor ) -> torch.Tensor: 
        # Apply topk logit encoding for gradients.
        return backward_request_gradient

    def decode_backward_request_gradient ( self, backward_request_gradient: torch.Tensor ) -> torch.Tensor:
        # Decode topk logit encoding for gradients.
        return backward_request_gradient

    def nill_forward_response_tensor( self, forward_request_tensor: torch.Tensor ) -> torch.Tensor:
        """ Returns a zeroed tensor used as response to a dendrite forward call when the call fails."""
        return torch.zeros( ( forward_request_tensor.size(0), forward_request_tensor.size(1), bittensor.__vocab_size__ ), dtype=torch.float32)

    def nill_backward_response_gradient( self, forward_request_tensor: torch.Tensor ) -> torch.Tensor:
        """ Returns a zeroed tensor used as response to a dendrite backward call when the call fails."""
        return torch.zeros( ( forward_request_tensor.size(0), forward_request_tensor.size(1), forward_request_tensor.size(2) ), dtype=torch.float32)
