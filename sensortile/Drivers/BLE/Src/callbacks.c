/*
 * callbacks.c
 *
 *  Created on: Mar 2, 2021
 *  Author: Silvano Cortesi
 */

#include "app_ble.h"
#include "bluenrg_gatt_aci.h"
#include "callbacks.h"
#include "services.h"

static volatile uint8_t connected = 0;
static uint16_t connection_handle = 0;

static service_cb_handler_t *local_service_callbacks = NULL;
static uint8_t local_service_callbacks_length = 0;

/**
 * Function which initalizes the local_service_callbacks variable by assigning a pointer
 * @param arg_service_callbacks pointer to an array which contains the service callback functions
 * @param arg_service_callbacks_length length of the array
 */
void set_cb_functions(service_cb_handler_t *arg_service_callbacks,
		uint8_t arg_service_callbacks_length) {
	local_service_callbacks = arg_service_callbacks;
	local_service_callbacks_length = arg_service_callbacks_length;
}

/**
 * Function to check whether the BLE is connected to a central
 * @return 1 if connected, else 0
 */
uint8_t is_connected(void) {
	return connected;
}

/**
 * Callback function called by event handler once a connection is established
 * @param peer_addr address of the central
 * @param handle handle to the connection
 */
void cb_on_gap_connection_complete(uint8_t peer_addr[], uint16_t handle) {
	connected = 1;
	connection_handle = handle;

	clear_connectable_status();
}

/**
 * Callback function called by event handler once a connection is terminated
 */
void cb_on_gap_disconnection_complete(void) {
	connected = 0;
	connection_handle = 0;

	// Disable all notifications for all services and characteristics
	for (uint8_t i = 0; i < local_service_callbacks_length; i++) {
		for (uint8_t j = 0;	j < sizeof(local_service_callbacks[i].characteristic_callbacks) / sizeof(characteristic_cb_handler_t); j++) {
			local_service_callbacks[i].characteristic_callbacks[j].notification_enabled = 0;
		}
	}

	set_connectable_status();
}

/**
 * Callback function called when a characteristic read is requested
 * @param handle handle to the request
 */
void cb_on_read_request(uint16_t handle) {

	// Iterate over all services and characteristics to find whose read handle is requested
	for (uint8_t i = 0; i < local_service_callbacks_length; i++) {
		for (uint8_t j = 0; j < sizeof(local_service_callbacks[i].characteristic_callbacks)	/ sizeof(characteristic_cb_handler_t); j++) {
			if (local_service_callbacks[i].characteristic_callbacks[j].characteristic_handler + 1 == handle) {
				if (local_service_callbacks[i].characteristic_callbacks[j].read	!= NULL) {
					local_service_callbacks[i].characteristic_callbacks[j].read(&local_service_callbacks[i]);
				}
			}
		}
	}

	if (connected && connection_handle != 0) {
		aci_gatt_allow_read(connection_handle);
	}
}

/**
 * Callback function called when a characteristic attribute modify is requested, especially a write or notifiy request
 * @param handle handle to the request
 */
void cb_on_attribute_modified(uint16_t handle, uint8_t len, uint8_t data[]) {

	// Iterate over all services and characteristics to find whose notify or write handle is requested
	for (uint8_t i = 0; i < local_service_callbacks_length; i++) {
		for (uint8_t j = 0;	j < sizeof(local_service_callbacks[i].characteristic_callbacks)	/ sizeof(characteristic_cb_handler_t); j++) {
			// If notification modified
			if (local_service_callbacks[i].characteristic_callbacks[j].characteristic_handler + 2 == handle) {
				if (data[0] == 0x01) {
					local_service_callbacks[i].characteristic_callbacks[j].notification_enabled = 1;
				} else {
					local_service_callbacks[i].characteristic_callbacks[j].notification_enabled = 0;
				}
			}
			// Else if write request
			else if (local_service_callbacks[i].characteristic_callbacks[j].characteristic_handler + 1 == handle) {
				if (local_service_callbacks[i].characteristic_callbacks[j].write != NULL)
					local_service_callbacks[i].characteristic_callbacks[j].write(&local_service_callbacks[i], len, data);
			}
		}
	}
}

/**
 * Function polled by the MX_BlueNRG_MS_Process function, sends all notifications which are pending
 */
void send_notification(void) {

	// Iterate over all services and characteristics to find ones with a pending notification
	for (uint8_t i = 0; i < local_service_callbacks_length; i++) {
		for (uint8_t j = 0; j < sizeof(local_service_callbacks[i].characteristic_callbacks) / sizeof(characteristic_cb_handler_t); j++) {
			if (local_service_callbacks[i].characteristic_callbacks[j].notification_enabled	&&
					*(local_service_callbacks[i].characteristic_callbacks[j].notification_pending) &&
					local_service_callbacks[i].characteristic_callbacks[j].notify != NULL) {

				local_service_callbacks[i].characteristic_callbacks[j].notify(&local_service_callbacks[i]);

				*(local_service_callbacks[i].characteristic_callbacks[j].notification_pending) = 0;
			}
		}
	}
}
