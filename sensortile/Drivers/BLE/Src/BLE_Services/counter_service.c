/*
 * counter_service.c
 *
 *  Created on: 11 Mar 2021
 *  Author: Silvano Cortesi
 */

#include <BLE_Services/counter_service.h>
#include "bluenrg_gatt_aci.h"
#include "bluenrg_conf.h"
#include <stdint.h>

// Conuter Service UUID (defined by BLE specification)
// const uint8_t counter_service_uuid[16] = { 0x23, 0x33, 0x10, 0x72, 0xa1, 0x43, 0x11, 0xeb, 0xbc, 0xbc, 0x02, 0x42, 0xac, 0x13, 0x00, 0x02 };
const uint8_t counter_service_uuid[16] = { 0x7a, 0xe5, 0x0c, 0x3d, 0xa2, 0x0a, 0xa8, 0x9a, 0x12, 0x41, 0x62, 0x55, 0x01, 0x40, 0x4a, 0xad };


// Counter 1 Characteristic UUID (defined by BLE specification)
//const uint8_t counter_1_char_uuid[16] = { 0x24, 0x33, 0x10, 0x72, 0xa1, 0x43, 0x11, 0xeb, 0xbc, 0xbc, 0x02, 0x42, 0xac, 0x13, 0x00, 0x02 };
const uint8_t counter_1_char_uuid[16] = { 0x7a, 0xe5, 0x0c, 0x3d, 0xa2, 0x0a, 0xa8, 0x9a, 0x12, 0x41, 0x62, 0x55, 0x41, 0x40, 0x4a, 0xad };

// Counter 2 Characteristic UUID (defined by BLE specification)
const uint8_t counter_2_char_uuid[16] = { 0x25, 0x33, 0x10, 0x72, 0xa1, 0x43, 0x11, 0xeb, 0xbc, 0xbc, 0x02, 0x42, 0xac, 0x13, 0x00, 0x02 };

// Notification pending bytes, passed as reference to callback. Will be 1 if a notification is pending
uint8_t counter_1_notification_pending = 0;
uint8_t counter_2_notification_pending = 0;

// Internal storage for the counter values, which is transmitted on read/notify request
static uint32_t counter_1 = 0;
static uint32_t counter_2 = 0;
static uint32_t counter = 0;
static uint32_t errors[100][2] = {{0}};
static uint32_t i = 1;
static uint32_t 
+[500][3] = {{0}};


/**
 * Function which sets a new value for the counter 1 and puts a new notification into the queue
 * @param value value as uint32_t which should be sent
 */
void set_counter_1_characteristic(uint32_t value) {
	// If a new value arrives, store it and set the notification to be pending
	if (value != counter_1) {
		counter_1 = value;
		counter_1_notification_pending = 1;
	}
}

/**
 * Function which sets a new value for the counter 2 and puts a new notification into the queue
 * @param value value as uint32_t which should be sent
 */
void set_counter_2_characteristic(uint32_t value) {
	// If a new value arrives, store it and set the notification to be pending
	if (value != counter_2) {
		counter_2 = value;
		counter_2_notification_pending = 1;
	}
}

/**
 * Read (and notify) function for the counter_1 characteristic
 * @param service_callback callback struct to the service, containing all handlers for the service and the characteristic (and pointers to the callback functions)
 * @param len length of the received data
 * @param data pointer to the received data
 */
void send_counter_1(service_cb_handler_t *service_callback) {
	// If a central is connected
	if (is_connected()) {
		// Create a buffer to convert the float into a bytearray
		uint8_t buffer[20] = { 0 };

		// Parse the pressure value into the byte array
		BLUENRG_memcpy(buffer, &counter_1, sizeof(buffer));

		// Transmit the pressure value
		uint8_t ret_val = aci_gatt_update_char_value(service_callback->service_handler, service_callback->characteristic_callbacks[0].characteristic_handler,	0, sizeof(buffer), buffer);
		//timestamp[i][0] =  HAL_GetTick();
		//timestamp[i][1] = timestamp[i][0] - timestamp[i-1][0];
		//timestamp[i][2] = counter_1;
		i++;
		if (ret_val != 0) {
			errors[counter][0] = ret_val;
			errors[counter][1] = counter_1;
			counter++; }
		if (counter == 100)					// If 100 notifications are failed to be received correctly. Will stop.
			while(1)
			{

			}
	}
}

/**
 * Read (and notify) function for the counter_2 characteristic
 * @param service_callback callback struct to the service, containing all handlers for the service and the characteristic (and pointers to the callback functions)
 * @param len length of the received data
 * @param data pointer to the received data
 */
void send_counter_2(service_cb_handler_t *service_callback) {
	// If a central is connected
	if (is_connected()) {
		// Create a buffer to convert the float into a bytearray
		uint8_t buffer[4] = { 0 };

		// Parse the pressure value into the byte array
		BLUENRG_memcpy(buffer, &counter_2, sizeof(buffer));

		// Transmit the pressure value
		uint8_t ret_val = aci_gatt_update_char_value(service_callback->service_handler, service_callback->characteristic_callbacks[1].characteristic_handler,	0, sizeof(buffer), buffer);
		if (ret_val != 0) {
			errors[counter][0] = ret_val;
			errors[counter][1] = counter_2;
			counter++; }
		if (counter == 100)
			while(1)
			{

			}
	}
}

/**
 * Function which adds the Counter service to the GATT server
 * @param service_callback callback struct to the service, containing all handlers for the service and the characteristic (and pointers to the callback functions)
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus add_counter_service(service_cb_handler_t *service_callback) {
	tBleStatus ret_val;

	// Copy pointers to handles of the service and the different characteristics
	uint16_t *counter_service_handle = &service_callback->service_handler;
	uint16_t *counter_1_characteristic_handle = &service_callback->characteristic_callbacks[0].characteristic_handler;
	uint16_t *counter_2_characteristic_handle = &service_callback->characteristic_callbacks[1].characteristic_handler;

	// Add the serivce to the GATT server using its UUID (16bit). Store its handle into the previously defined pointer.
	// Configure it as primary service, having a max. of 7 attributes
	ret_val = aci_gatt_add_serv(UUID_TYPE_128, counter_service_uuid, PRIMARY_SERVICE, 0x07, counter_service_handle);
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Add the counter_1 characteristic to the service stored in the service_handle. Store its handle into the previously defined pointer.
	// The characteristic consists of 5bytes, has possibility for NOTIFY and READ, needs no bonding/permission.
	ret_val = aci_gatt_add_char(*counter_service_handle, UUID_TYPE_128, counter_1_char_uuid, 20, CHAR_PROP_NOTIFY | CHAR_PROP_READ,
			ATTR_PERMISSION_NONE, GATT_NOTIFY_READ_REQ_AND_WAIT_FOR_APPL_RESP, 16, 1, counter_1_characteristic_handle);
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Store the characteristics callback functions in the callback struct, s.t. the event handler can call it
	service_callback->characteristic_callbacks[0].read = send_counter_1;
	service_callback->characteristic_callbacks[0].notify = send_counter_1;
	service_callback->characteristic_callbacks[0].notification_pending = &counter_1_notification_pending;

	// Add the counter_2 characteristic to the service stored in the service_handle. Store its handle into the previously defined pointer.
	// The characteristic consists of 4bytes, has possibility for NOTIFY and READ, needs no bonding/permission.
	ret_val = aci_gatt_add_char(*counter_service_handle, UUID_TYPE_128, counter_2_char_uuid, 4,	CHAR_PROP_NOTIFY | CHAR_PROP_READ,
			ATTR_PERMISSION_NONE, GATT_NOTIFY_READ_REQ_AND_WAIT_FOR_APPL_RESP, 16, 1, counter_2_characteristic_handle);
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Store the characteristics callback functions in the callback struct, s.t. the event handler can call it
	service_callback->characteristic_callbacks[1].read = send_counter_2;
	service_callback->characteristic_callbacks[1].notify = send_counter_2;
	service_callback->characteristic_callbacks[1].notification_pending = &counter_2_notification_pending;

	return ret_val;
}
