# -*- coding: utf-8 -*-
import math
import time
import numpy

def normalizeMax(dataList, maxValue):
	values = []
	maxValue = float(maxValue)
	for x in dataList:
		try:
			v = x/maxValue
		except ZeroDivisionError:
			v = 0
		values.append(v)
	return values


def roundMetric(metric, offset):
	metric = int(math.ceil(metric/offset)*offset)
	return metric
