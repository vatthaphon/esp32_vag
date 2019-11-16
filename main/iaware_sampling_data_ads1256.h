#ifndef IAWARE_SAMPLING_DATA_ADS1256_H
#define IAWARE_SAMPLING_DATA_ADS1256_H

// Do not forget to change ADS1256_VSPI_init(SPI_BUS_SCLK_1M, ADS1256_ADDR_REG_DRATE_15000SPS);
#define SAMPLING_DATA_FS 15000
// #define SAMPLING_DATA_FS 7500
// #define SAMPLING_DATA_FS 1000

extern uint32_t sampling_data_fs;	// The sampling frequency of the signal.

void init_sampling_data_ads1256_task(void);
void start_sampling_data_ads1256(void);

void init_buff_nodes(void);

#endif