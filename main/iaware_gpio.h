#ifndef IAWARE_GPIO_H
#define IAWARE_GPIO_H

#include "driver/adc.h"
#include "driver/gpio.h"
#include "esp_adc_cal.h"


#define GPIO_OUTPUT_LOW 	0
#define GPIO_OUTPUT_HIGH 	1

#define GPIO_LED_ONBOARD 	GPIO_NUM_2

// Attenuation refers to the amount an voltage signal is scaled down before being input into the ADC.  The ADC's can ideally only measure voltages 
// between 0 to 1100mV. Therefore to measure voltages larger than 1100mV, an input voltage can be scaled down such that it is within the 0 to 1100mV 
// range hence giving the ADC a larger effective voltage range.

// src. https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/peripherals/adc.html#_CPPv411adc_atten_t
// The default ADC full-scale voltage is 1.1V. To read higher voltages (up to the pin maximum voltage, usually 3.3V) requires setting >0dB signal 
// attenuation for that ADC channel.

// When VDD_A is 3.3V:
	// 0dB attenuaton 		(ADC_ATTEN_DB_0) 	between 100 and 950mV
	// 2.5dB attenuation	(ADC_ATTEN_DB_2_5) 	between 100 and 1250mV
	// 6dB attenuation 		(ADC_ATTEN_DB_6) 	between 150 and 1750mV
	// 11dB attenuation 	(ADC_ATTEN_DB_11) 	between 150 and 2450mV

#define GPIO_ADC_WIDTH_BIT  ADC_WIDTH_BIT_12
// #define GPIO_ADC_ATTEN_DB	ADC_ATTEN_DB_0
#define GPIO_ADC_ATTEN_DB	ADC_ATTEN_DB_11
#define GPIO_REF_VOLTAGE 	1100 // [mV]

extern esp_adc_cal_characteristics_t *adc_chars;

uint16_t iaware_analogRead(void);
void iaware_init_gpio(void);

void turn_on_LED_ONBOARD(void);
void turn_off_LED_ONBOARD(void);

void led_onboard_ap_start(void);
void led_onboard_ap_stop(void);
void led_onboard_client_connected(void);
void led_onboard_client_disconnected(void);
void led_onboard_send_data_to_client(void);

#endif