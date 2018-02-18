# -*- coding: utf-8 -*-

import datetime

def _parse_date_format( fmp_database ):
	"""Builds format string to pass to strptime from the datetime module.

    fmp_database is the result of the 
    self.database = self.doGetXMLAttributes(node)
    called on the "datasource" node of the retruned xml.
    """
	def build_one( stamp ):
		return stamp.\
		  replace( 'yyyy', '%Y' ).\
		  replace( 'MM', '%m' ).\
		  replace( 'dd', '%d' ).\
		  replace( 'HH', '%H' ).\
		  replace( 'mm', '%M' ).\
		  replace( 'ss', '%S' )

	return {
		'date': build_one( fmp_database.get('date-format', '') ),
		'timestamp': build_one( fmp_database.get('timestamp-format', '') ),
		'time': build_one( fmp_database.get('time-format', '') ),
	}

class TypeCaster(dict):
	"""
    A dict of function to cast fmp data to the correct type.

    It recieves the metadata and datasource node from the xml.

	Possible types are (from fmp xml doc):
     “text”, “number”, “date”, “time”, “timestamp”, or “container”
	"""
	timestamps_default = {
		'date': '%m/%d/%Y',
		'time': '%H:%M:%S',
		'timestamp': '%m/%d/%Y %H:%M:%S',
	}

	def __init__( self ):
		super( TypeCaster, self ).__init__()
		self.timeformats = self.__class__.timestamps_default
		self.is_initialized = False
		self.multivalues = dict()
    
	def initialize( self, meta, timeformats ):
		f = _parse_date_format( timeformats )
		self.timeformats = f

		for key, value in meta.items():
			r = int( value.get('max-repeat', 1 ) )
			t = value.get('result', 'text' )

			func = self._get_type( field_type=t )
			self.multivalues[key] = r
			self[key] = func
		self.is_initialized = True

	def get_text( self, value ):
		return value

	def get_float( self, value ):
		try:
			return float( value )
		except Exception:
			pass
		return ''

	def get_date( self, value ):
		try:
			return datetime.datetime.strptime( 
				value, 
				self.timeformats['date'],
			).date()
		except ValueError:
			return ''

	def get_time( self, value ):
		try:
			return datetime.datetime.strptime( 
				value,
				self.timeformats['time'],
			).time()
		except ValueError:
			return ''

	def get_timestamp( self, value ):
		try:
			return datetime.datetime.strptime( 
				value, 
				self.timeformats['timestamp'],
			)
		except ValueError:
			return ''


	def as_date( self, value ):
		f = self.timeformats
		return value.strftime( f['date'] )

	def as_time( self, value ):
		f = self.timeformats
		return value.strftime( f['time'] )

	def as_timestamp( self, value ):
		f = self.timeformats
		return value.strftime( f['timestamp'] )

	def _get_type( self, field_type ):
		if field_type == 'text':
			return self.get_text

		elif field_type == 'number':
			return self.get_float

		elif field_type == 'container':
			return lambda x:x

		elif field_type == 'timestamp':
			return self.get_timestamp

		elif field_type == 'date':
			return self.get_date

		elif field_type == 'time':
			return self.get_time
