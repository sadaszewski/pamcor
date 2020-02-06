from pamcor.learning.nn import Conv2D, \
    Dense
from torch.nn.functional import conv2d, \
    relu
from torch import tensor
import numpy as np


def test_01_Conv2D():
    cv = Conv2D(out_channels=32, kernel_size=8,
        stride=4, activation=relu)
    im = np.random.random((3, 64, 64))
    print('im.shape:', im.shape)
    res = cv(im)
    print('res.shape:', res.shape)

    im = im.reshape((1, 3, 64, 64))
    im = tensor(im)
    res_1 = conv2d(im, cv.weight, stride=4)

    assert (res == res_1).all()


def test_02_Conv2D_many():
    cv1 = Conv2D(out_channels=32, kernel_size=8,
        stride=4, activation=relu)
    cv2 = Conv2D(out_channels=64, kernel_size=4,
        stride=2, activation=relu)
    cv3 = Conv2D(out_channels=64, kernel_size=3,
        stride=1)
    im = np.random.random((4, 64, 64))
    res = cv1(im)
    print('#1 res.shape:', res.shape)
    res = cv2(res)
    print('#2 res.shape:', res.shape)
    res = cv3(res)
    print('#3 res.shape:', res.shape)

    assert res.shape == (1, 64, 4, 4)

    return res


def test_03_flatten():
    res = test_02_Conv2D_many()
    res = res.flatten()
    print('res.shape:', res.shape)
    assert res.shape == (1 * 64 * 4 * 4,)


def test_04_Dense():
    d1 = Dense(5, activation=relu)
    input = np.random.random((64 * 4 * 4,))
    res = d1(input)
    print('res.shape:', res.shape)
    assert res.shape == (1, 5)


def test_05_Dense_batch():
    d1 = Dense(5, activation=relu)
    input = np.random.random((55, 64 * 4 * 4,))
    res = d1(input)
    print('res.shape:', res.shape)
    assert res.shape == (55, 5)
