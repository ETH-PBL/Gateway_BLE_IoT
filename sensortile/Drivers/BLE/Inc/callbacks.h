/*
 * callbacks.h
 *
 *  Created on: Mar 2, 2021
 *  Author: Silvano Cortesi
 */

#ifndef INC_CALLBACKS_H_
#define INC_CALLBACKS_H_

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

// Maximum number of characteristics per service
#define MAX_NUMBER_OF_CHARACTERISTICS 6
// Maximum number of characteristics per service
#define MAX_NUMBER_OF_CHARACTERISTIC_DESCRIPTIONS 6

#define BLE_ERROR_OUT_OF_MEMORY 0x1F

typedef struct _characteristic_cb_handler characteristic_cb_handler_t;
typedef struct _service_cb_handler service_cb_handler_t;

// Struct containing handlers of a characteristic as well as callback functions
typedef struct _characteristic_cb_handler {
	uint16_t characteristic_handler;
	uint16_t characteristic_description_handler[MAX_NUMBER_OF_CHARACTERISTIC_DESCRIPTIONS];
	void (*write)(service_cb_handler_t *service_callback, uint8_t len,
			uint8_t data[]);
	void (*read)(service_cb_handler_t *service_callback);
	void (*notify)(service_cb_handler_t *service_callback);
	uint8_t notification_enabled;
	uint8_t *notification_pending; // passed as reference from callback of services
} characteristic_cb_handler_t;

// Struct containing handler of a service, as well as an array containing all characteristic callback functions and handlers
typedef struct _service_cb_handler {
	uint16_t service_handler;
	characteristic_cb_handler_t characteristic_callbacks[MAX_NUMBER_OF_CHARACTERISTICS];
} service_cb_handler_t;

/**
 * Function which initalizes the local_service_callbacks variable by assigning a pointer
 * @param arg_service_callbacks pointer to an array which contains the service callback functions
 * @param arg_service_callbacks_length length of the array
 */
void set_cb_functions(service_cb_handler_t *arg_service_callbacks,
		uint8_t arg_service_callbacks_length);

/**
 * Function to check whether the BLE is connected to a central
 * @return 1 if connected, else 0
 */
uint8_t is_connected(void);

/**
 * Callback function called by event handler once a connection is established
 * @param peer_addr address of the central
 * @param handle handle to the connection
 */
void cb_on_gap_connection_complete(uint8_t*, uint16_t);

/**
 * Callback function called by event handler once a connection is terminated
 */
void cb_on_gap_disconnection_complete(void);

/**
 * Callback function called when a characteristic read is requested
 * @param handle handle to the request
 */
void cb_on_read_request(uint16_t);

/**
 * Callback function called when a characteristic attribute modify is requested, especially a write or notifiy request
 * @param handle handle to the request
 */
void cb_on_attribute_modified(uint16_t, uint8_t, uint8_t[]);

/**
 * Function polled by the MX_BlueNRG_MS_Process function, sends all notifications which are pending
 */
void send_notification(void);

#ifdef __cplusplus
}
#endif

#endif /* INC_CALLBACKS_H_ */
