/*
 * services.c
 *
 *  Created on: Mar 2, 2021
 *  Author: Silvano Cortesi
 */

#include <BLE_Services/counter_service.h>
#include "callbacks.h"
#include "services.h"

// Initialize struct for the service callbacks. Should be as large as the total amount of services
service_cb_handler_t service_callbacks[1];

/**
 * Initialization functions for the different services
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus add_services(void) {
	tBleStatus ret_val = BLE_STATUS_SUCCESS;

	// Add the Environmental Service to the GATT server, store its callback in the array
	ret_val = add_counter_service(&service_callbacks[0]);
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Provide informations about the service callbacks to the callbacks handler
	set_cb_functions(service_callbacks,	sizeof(service_callbacks) / sizeof(service_cb_handler_t));

	return ret_val;
}
