from torch import tensor
from torch.nn.functional import conv2d, \
    relu, linear
from torch import Tensor
import numpy as np


class Conv2D(object):
    def __init__(self, out_channels, kernel_size, stride,
        activation=relu, groups=1, initial_weight_multiplier=0.01):

        try:
            kernel_size = [a for a in kernel_size]
        except TypeError:
            kernel_size = [kernel_size,] * 2

        if len(kernel_size) != 2:
            raise ValueError(f'Expected 2 elements in kernel_size, ' + \
                'got: {len(kernel_size)}')

        self.out_channels = out_channels
        self.kernel_size = kernel_size
        self.stride = stride
        self.activation = activation
        self.groups = 1
        self.weight = None
        self.initial_weight_multiplier = initial_weight_multiplier

    def clone(self):
        res = Conv2D(self.out_channels, self.kernel_size,
            self.stride, self.activation, self.groups)
        if self.weight is not None:
            res.weight = self.weight.clone().detach().requires_grad_(True)
        return res

    def create_weight(self, input_):
        out_channels, kernel_size, stride, activation, groups = \
            self.out_channels, self.kernel_size, self.stride, \
            self.activation, self.groups
        in_channels = input_.shape[-3]
        if in_channels / groups != in_channels // groups:
            raise ValueError('in_channels must be divisible by groups')
        weight = np.random.random([out_channels, in_channels // groups] + \
            self.kernel_size).astype(np.float32) * self.initial_weight_multiplier
        weight = tensor(weight, requires_grad=True)
        return weight

    def __call__(self, input_):
        input_ = input_.reshape((1,) * (4 - len(input_.shape)) + input_.shape)
        if not isinstance(input_, Tensor):
            input_ = tensor(input_, requires_grad=False)
        if self.weight is None:
            self.weight = self.create_weight(input_)
        res = conv2d(input_, self.weight, stride=self.stride)
        if self.activation is not None:
            res = self.activation(res)
        return res


class Dense(object):
    def __init__(self, out_features, activation=relu,
        initial_weight_multiplier=0.01):
        self.out_features = out_features
        self.activation = activation
        self.in_features = None
        self.weight = None
        self.initial_weight_multiplier = initial_weight_multiplier

    def clone(self):
        res = Dense(self.out_features, self.activation)
        res.in_features = self.in_features
        if self.weight is not None:
            res.weight = self.weight.clone().detach().requires_grad_(True)
        return res

    def __call__(self, input_):
        in_features = input_.shape[-1]

        if self.weight is None:
            self.in_features = in_features
            weight = np.random.random((self.out_features,
                in_features)).astype(np.float32) * self.initial_weight_multiplier
            self.weight = tensor(weight, requires_grad=True)

        if len(input_.shape) == 1:
            input_ = input_.reshape((1,) + input_.shape)

        if not isinstance(input_, Tensor):
            input_ = tensor(input_, requires_grad=False)

        res = linear(input_, self.weight)
        if self.activation is not None:
            res = self.activation(res)

        return res
