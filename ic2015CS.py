#!/bin/python
'''Monitorizacion de la tension y carga de una bateria de litio a travesdel IC CW2015
para un escudo Raspi UPS Hat
http://www.cellwise-semi.com/en/ProductView.asp?ID=154
http://www.raspberrypiwiki.com/index.php/Power_Pack_Pro
'''

import struct
import smbus
import sys
import time

# Pone en marcha si es necesario la funcion I2C y lee todos los registros del CW2015
def configUPS():
	if bus.read_byte_data(0x62, 0x0A) ==0xC0:
		print "Habilitamos IC.."
		bus.write_byte_data(0x62, 0x0A, 0x00) 
		time.sleep(2)
	for i in range(0,11, 2):                                            # del 0 al 10 en incrementos de 2
		print "Valor leido del registro %d: %x" %(i, bus.read_word_data(0x62, i))
	print"----------------------------------------"
# Pasa a reposo
def reposo():
	print "IC en reposo.."
	bus.write_byte_data(0x62, 0x0A, 0xC0)                               # 0001100 bits QSTRT0 y QSTRT1 a 1
	
# retorna la tension de floatacion 
def RxTension(bus):
	lectura = bus.read_word_data(0x62, 2)                               # leemos el registro 2
	rotado = struct.unpack("<H", struct.pack(">H", lectura))[0]         # leemos y intercambiamos bytes alto por el bajo
	tension = rotado * 305                                              # obtenemos la tension en uV
	tension = tension/1000000.0                                         # realizamos el calculo para pasa a voltios
	return tension

# Retorna el porcentaje de capacidad de la bateria
def RxCapacidad(bus):
	lectura = bus.read_word_data(0x62, 4)
	return bus.read_byte_data(0x62, 0x04) + (bus.read_byte_data(0x62, 0x05) /100.0)

# Comprobamos si nos encontranos en aleta por baja carga de la bateria 
def Rxtime(bus):
	alerta = bus.read_word_data(0x62, 6) >>15
	if alerta:
		return
	print "!!Alerta por baja carga <4%!!"                               # defecto a 3%

#///////////////////////////////////////////////////////////////////////
bus = smbus.SMBus(1)  # 0 = /dev/i2c-0 (port I2C0), 1 = /dev/i2c-1 (port I2C1)

configUPS()
try:
	while True:
		TensionBat =RxTension(bus)
		CapacidadBat =RxCapacidad(bus)
		print "Tension de la bateria: %5.2fV" % TensionBat 
		print "El estado de carga de la bateria es del: %3.2f%%" % CapacidadBat
		time.sleep(60)
		Rxtime(bus)
except KeyboardInterrupt:
	reposo()
	print('Salimos!')


 


