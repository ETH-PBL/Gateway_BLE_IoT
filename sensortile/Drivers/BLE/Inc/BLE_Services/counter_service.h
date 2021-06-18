/*
 * counter_service.h
 *
 *  Created on: 11 Mar 2021
 *  Author: Silvano Cortesi
 */

#ifndef INC_COUNTER_SERVICE_H_
#define INC_COUNTER_SERVICE_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "bluenrg_def.h"
#include "callbacks.h"

/**
 * Function which adds the Counter service to the GATT server
 * @param service_callback callback struct to the service, containing all handlers for the service and the characteristic (and pointers to the callback functions)
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus add_counter_service(service_cb_handler_t *service_callback);

/**
 * Function which sets a new value for the counter 1 and puts a new notification into the queue
 * @param value value as uint32_t which should be sent
 */
void set_counter_1_characteristic(uint32_t value);

/**
 * Function which sets a new value for the counter 2 and puts a new notification into the queue
 * @param value value as uint32_t which should be sent
 */
void set_counter_2_characteristic(uint32_t value);

#ifdef __cplusplus
}
#endif

#endif /* INC_COUNTER_SERVICE_H_ */
