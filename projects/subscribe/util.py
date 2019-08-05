from scipy.stats import truncnorm

def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
	return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)


def meter_to_miles(meter):
	return meter/1609.34


def mps_to_Mph(mps):
	return ((mps * 3600)/1609.34)