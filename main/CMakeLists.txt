# Edit following two lines to set component requirements (see docs)
set(COMPONENT_REQUIRES )
set(COMPONENT_PRIV_REQUIRES )

set(COMPONENT_SRCS 
"../../components/helper/helper.c"
"../../components/ads1256/ads1256.c"
"main.c" 
"iaware_helper.c" 
"iaware_tcp_com.c" 
"iaware_sampling_data_ads1256.c" 
"iaware_packet.c" 
"iaware_gpio.c")

set(COMPONENT_ADD_INCLUDEDIRS 
"../../components/helper/include" 
"../../components/ads1256/include" 
".")

register_component()


