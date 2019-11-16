#ifndef IAWARE_HELPER_H
#define IAWARE_HELPER_H

#include "esp_err.h"

#include "main.h"

struct buff_node
{
    struct buff_node *prev;

    uint8_t is_sent;

    uint8_t packet_header_group_id;

    uint8_t *samples_buff; // The unit of voltage is in mV.

    uint32_t n_samples; // It equals sizeof(samples_buff) - 4 (4 bytes equaling n_samples) - PACKET_HEADER_GROUPx_META_SIZE.
    uint32_t i_samples; // i_samples starts from 0 to n_samples - 1.

    struct buff_node *next;
};


int append_buff_node_group1(uint32_t elt_count);
void free_all_buff_node_group1(void);
void free_buff_node_group1(struct buff_node **curr_ptr);
void pop_buff_node_group1(void);
struct buff_node *buff_node_group1_alloc(uint32_t elt_count);

void free_null(void **ptr);

int getSSID(uint8_t *mac, char *ssid);

int x_printf_int(char *msg);
int x_printf(char *msg);

uint8_t highbyte(uint16_t num);
uint8_t lowbyte(uint16_t num);

uint16_t bytes_to_uint16(uint8_t a[]);

void uint32_to_bytes(uint32_t num, uint8_t a[]);
void uint64_to_bytes(uint64_t num, uint8_t a[]);

uint32_t bytes_to_uint32(uint8_t a[]);
uint64_t bytes_to_uint64(uint8_t a[]);


void double_to_bytes(double num, uint8_t a[]);
double bytes_to_double(uint8_t a[]);

void float_to_bytes(float num, uint8_t a[]);
float bytes_to_float(uint8_t a[]);

void str_to_uuid128(uint8_t uuid128[], char uuid128_str[]);

const char* err_to_str(esp_err_t err);

uint8_t get_battery_level(void);

#endif


