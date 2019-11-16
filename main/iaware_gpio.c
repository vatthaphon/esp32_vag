// Choose idf.py menuconfig->Component config->Wi-FI->WiFi Task Core ID->Core 1
// Choose idf.py menuconfig->Component config->LWIP->TCP/IP task affinity ->CPU1
// Choose idf.py menuconfig->Component config->ESP32-specific->disable Watch CPU0 Idel Task
// Choose idf.py menuconfig->Component config->ESP32-specific->disable Watch CPU1 Idel Task

#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "driver/adc.h"
#include "driver/gpio.h"
#include "esp_adc_cal.h"
#include "esp_log.h"
#include "esp_system.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "iaware_gpio.h"
#include "main.h"

esp_adc_cal_characteristics_t *adc_chars = NULL;

void iaware_init_gpio(void)
//GPIOs, src: https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/peripherals/adc.html
{

    // Initializa the onboard LED.
    gpio_pad_select_gpio(GPIO_LED_ONBOARD);
    gpio_set_direction(GPIO_LED_ONBOARD, GPIO_MODE_OUTPUT);

    turn_off_LED_ONBOARD();


    // Because we use WiFI, we should not use ADC2.
    // Note that even the hall sensor is internal to ESP32, reading from it uses channels 0 and 3 of ADC1 (GPIO 36 and 39)
    // ULP (Ultra Low Power) coprocessor is a simple FSM which is designed to perform measurements using ADC, temperature sensor, and external I2C sensors, 
    // while main processors are in deep sleep mode. 
    adc1_config_width(GPIO_ADC_WIDTH_BIT);

    if ((adc_chars = (esp_adc_cal_characteristics_t *) calloc(1, sizeof(esp_adc_cal_characteristics_t))) == NULL)
    {
        ESP_LOGE(IAWARE_GPIO, "Fail to allocate a memory for esp_adc_cal_characteristics_t.");
    }

    adc1_config_channel_atten(ADC1_CHANNEL_0, GPIO_ADC_ATTEN_DB);

    esp_adc_cal_characterize(ADC_UNIT_1, GPIO_ADC_ATTEN_DB, GPIO_ADC_WIDTH_BIT, GPIO_REF_VOLTAGE, adc_chars);    
     
    int64_t pre_time = esp_timer_get_time();
    
    iaware_analogRead();

    ESP_LOGW(IAWARE_GPIO, "Main: adc1_get_raw use %" PRId64 " microsec.", (esp_timer_get_time() - pre_time));   
}

uint16_t iaware_analogRead(void)
{
    uint16_t val = (uint16_t) esp_adc_cal_raw_to_voltage(adc1_get_raw(ADC1_CHANNEL_0), adc_chars);
    // printf("%d\n", val);

    return val;
}

void led_onboard_send_data_to_client(void)
{
    // turn_off_LED_ONBOARD();
    //     vTaskDelay(1 / portTICK_PERIOD_MS);    

    // turn_on_LED_ONBOARD();
}

void led_onboard_client_connected(void)
{
    // turn_off_LED_ONBOARD();
    //     vTaskDelay(500 / portTICK_PERIOD_MS);    
    // turn_on_LED_ONBOARD();
    //     vTaskDelay(500 / portTICK_PERIOD_MS);
    // turn_off_LED_ONBOARD();
    //     vTaskDelay(500 / portTICK_PERIOD_MS);    
    // turn_on_LED_ONBOARD();
    //     vTaskDelay(500 / portTICK_PERIOD_MS);
    // turn_off_LED_ONBOARD();
    //     vTaskDelay(500 / portTICK_PERIOD_MS);

    turn_on_LED_ONBOARD();
}

void led_onboard_client_disconnected(void)
{
    turn_off_LED_ONBOARD();
}

void led_onboard_ap_start(void)
{
    // turn_on_LED_ONBOARD();
    turn_off_LED_ONBOARD();
}

void led_onboard_ap_stop(void)
{
    turn_off_LED_ONBOARD();
}


void turn_on_LED_ONBOARD(void)
{
    gpio_set_level(GPIO_LED_ONBOARD, GPIO_OUTPUT_HIGH);    
}

void turn_off_LED_ONBOARD(void)
{
    gpio_set_level(GPIO_LED_ONBOARD, GPIO_OUTPUT_LOW);       
}

