#include <inttypes.h>
#include <stdio.h>

#include "esp_timer.h"
#include "esp_sleep.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#include "ads1256.h"

#include "iaware_gpio.h"
#include "iaware_helper.h"
#include "iaware_packet.h"
#include "iaware_sampling_data_ads1256.h"
#include "iaware_tcp_com.h"
#include "main.h"

uint32_t sampling_data_fs = SAMPLING_DATA_FS;

// uint32_t sampling_data_fs = ADS1256_ADDR_REG_DRATE_7500SPS;

// #define SAMPLING_DATA_FS ADS1256_ADDR_REG_DRATE_15000SPS
// #define SAMPLING_DATA_FS ADS1256_ADDR_REG_DRATE_7500SPS


void init_sampling_data_ads1256_task(void)
{
    ESP_LOGI(IAWARE_CORE, "VSPI run at Core %d.", xPortGetCoreID());

    // Initialize buffer nodes.
    init_buff_nodes();

    // Initialize ADS1256.
    ADS1256_VSPI_init(SPI_BUS_SCLK_2M, ADS1256_ADDR_REG_DRATE_15000SPS);
    // ADS1256_VSPI_init(SPI_BUS_SCLK_1M, ADS1256_ADDR_REG_DRATE_15000SPS);
    // ADS1256_VSPI_init(SPI_BUS_SCLK_1M, ADS1256_ADDR_REG_DRATE_7500SPS);
    // ADS1256_VSPI_init(SPI_BUS_SCLK_1M, ADS1256_ADDR_REG_DRATE_1000SPS);
    
}

void init_buff_nodes(void)
{
    // Check free memory.
    // ESP_LOGI(IAWARE_CORE, "heap_caps_get_free_size(MALLOC_CAP_8BIT) = %d bytes, heap_caps_get_largest_free_block(MALLOC_CAP_8BIT) = %d bytes.", heap_caps_get_free_size(MALLOC_CAP_8BIT), heap_caps_get_largest_free_block(MALLOC_CAP_8BIT));

    uint32_t N_buff_node;
    // Create buffer nodes for filling in the sampled inputs.
    N_buff_node = (uint32_t) (TCP_MAX_LATENCY / (1000/tcp_send_frequency));

    ESP_LOGI(IAWARE_CORE, "Sample data: try to allocate %d buff nodes, of which each has %d samples.", N_buff_node, (uint32_t) (sampling_data_fs/tcp_send_frequency));

    uint32_t i = 0;
    while ((i < N_buff_node) & (append_buff_node_group1((uint32_t) (sampling_data_fs/tcp_send_frequency)) == iawTrue))
    {
        i = i + 1;
    }

    if (i == 0)
    {
        ESP_LOGE(IAWARE_CORE, "Sample data: Initialize buff_node (%d bytes) FAIL.", (uint32_t) (2*sampling_data_fs/tcp_send_frequency));
        deep_restart();
    }
    else
    {
        ESP_LOGI(IAWARE_CORE, "Sample data: Initialize buff_node (%d buff nodes = %d bytes).", i, (uint32_t) (i*2*sampling_data_fs/tcp_send_frequency));
    }
}

uint32_t cnt = 0;
// uint8_t dat[3];
void start_sampling_data_ads1256(void)
// This function should execute with using as least time as possible.
// Please read https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/system/wdts.html for further informaiton.
{
    ESP_LOGI(IAWARE_CORE, "VSPI run at Core %d.", xPortGetCoreID());

    // Activate ADS1256 to send the samples.
    // ADS1256_VSPI_start();
    // vTaskDelay(10 / portTICK_PERIOD_MS);

    while (1)
    {

        // ADS1256_VSPI_readInBytes(&( (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples)] ));

        ADS1256_VSPI_RDATA_readInBytes(&( (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples)] ));
        
        // (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples)] = 0;
        // cnt++;
        // if (cnt > 15000)
        // {
        //     cnt = 0;
            

        //     printf("%d,%d,%d\n", (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples)], (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples) + 1], (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples) + 2]);
        // }
        
        // if ((run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples)] == 0)
        // {
        // }
        // else
        // {
        //     printf("%d,%d,%d\n", (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples)], (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples) + 1], (run_buff_node_ptr->samples_buff)[4 + PACKET_HEADER_GROUP1_META_SIZE + (run_buff_node_ptr->i_samples) + 2]);            
        // }


        run_buff_node_ptr->i_samples += PACKET_HEADER_GROUP1_A_SAMPLE_SIZE_IN_BYTES;        

        if (run_buff_node_ptr->i_samples == run_buff_node_ptr->n_samples)
        {        
            struct buff_node *tmp_ptr = run_buff_node_ptr; // Guarantee thread safe.        

            // Move run_buff_node_ptr to the next node.
            if (run_buff_node_ptr->next != NULL)
            {
                run_buff_node_ptr = run_buff_node_ptr->next;
            }    
            else
            {
                // Reach the end of the buff nodes.
                run_buff_node_ptr = head_buff_node_ptr;
            }

            run_buff_node_ptr->i_samples = 0;     
            run_buff_node_ptr->is_sent = iawTrue;

            // Set bit to tell com_tcp_send_task() to send this buffer node.
            tmp_ptr->is_sent = iawFalse;
        }
    }
}
