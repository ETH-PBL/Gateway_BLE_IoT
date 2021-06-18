/*
 * app_ble.c
 *
 *  Created on: Mar 2, 2021
 *  Author: Silvano Cortesi
 */

#include "app_ble.h"
#include "bluenrg_aci_const.h"
#include "bluenrg_gap.h"
#include "bluenrg_gap_aci.h"
#include "bluenrg_gatt_aci.h"
#include "bluenrg_hal_aci.h"
#include "callbacks.h"
#include "hci.h"
#include "hci_le.h"
#include "services.h"
#include <stdint.h>

// Flag indicating if the device is connectable
static uint8_t connectable = 1;

/**
 * @brief Function called by event handler once a new connection should be established
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
static tBleStatus establish_connection(void);

/**
 * @brief Event handler on a BLE event, manages connections, advertising and handles read/write/notify requests
 * @param pData is the pointer to the BLE event
 */
void event_user_notify(void*);

/**
 * @brief Function to initialize BLE
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus MX_BlueNRG_MS_Init(void) {
	tBleStatus ret_val = BLE_STATUS_SUCCESS;

	const char *name = DEVICE_NAME;
	uint8_t bdaddr[BLUETOOTH_DEVICE_ADDRESS_SIZE] = BLUETOOTH_DEVICE_ADDRESS;

	uint16_t service_handle,
	dev_name_char_handle, appearance_char_handle;

	// Initialize the SPI and reset the module
	hci_init(&event_user_notify, NULL);
	ret_val = hci_reset();
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	HAL_Delay(100);

	// Configure BLE device address
	ret_val = aci_hal_write_config_data(CONFIG_DATA_PUBADDR_OFFSET, CONFIG_DATA_PUBADDR_LEN, bdaddr);
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Used BLE chip is IDB05A1
	// Initialize gatt
	ret_val = aci_gatt_init();
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Initialize GAP
	ret_val = aci_gap_init_IDB05A1(GAP_PERIPHERAL_ROLE_IDB05A1, 0, strlen(name), &service_handle, &dev_name_char_handle, &appearance_char_handle);
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Set name as characteristic value
	ret_val = aci_gatt_update_char_value(service_handle, dev_name_char_handle, 0, strlen(name), (uint8_t*) name);
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	// Initialize services
	ret_val = add_services();
	if (ret_val != BLE_STATUS_SUCCESS)
		return ret_val;

	return ret_val;
}

/**
 * @brief Process BLE events and send notifications
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus MX_BlueNRG_MS_Process(void) {
	tBleStatus ret_val = BLE_STATUS_SUCCESS;

	// If the device is connectable, try to establish a connection
	if (connectable == 1) {
		ret_val = establish_connection();
		if (ret_val != BLE_STATUS_SUCCESS)
			return ret_val;
	}

	// Send all pending notifications
	send_notification();

	// Handle all events
	hci_user_evt_proc();

	return ret_val;
}

/**
 * @brief Function to set the device into connectable mode
 */
void set_connectable_status(void) {
	connectable = 1;
}

/**
 * @brief Function to clear the connectable mode, stops advertising and starts the GATT server
 */
void clear_connectable_status(void) {
	connectable = 0;
}

/**
 * @brief Function called by event handler once a new connection should be established
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus establish_connection(void) {
	tBleStatus ret_val = BLE_STATUS_SUCCESS;

	// Set the device name
	char local_name[DEVICE_NAME_SIZE + 2] = { 0 };
	local_name[0] = AD_TYPE_COMPLETE_LOCAL_NAME;
	strncpy(&local_name[1], DEVICE_NAME, DEVICE_NAME_SIZE + 1);

	// Set the BLE scan response
	ret_val = hci_le_set_scan_resp_data(0, NULL);
	if ((ret_val != BLE_STATUS_SUCCESS) && (ret_val != ERR_COMMAND_DISALLOWED))
		return ret_val;

	// Set the device as discoverable
	ret_val = aci_gap_set_discoverable(ADV_IND, 0, 0, PUBLIC_ADDR,
	NO_WHITE_LIST_USE, DEVICE_NAME_SIZE + 1, local_name, 0,
	NULL, 0, 0);
	if ((ret_val != BLE_STATUS_SUCCESS) && (ret_val != ERR_COMMAND_DISALLOWED))
		return ret_val;

	if (ret_val == ERR_COMMAND_DISALLOWED)
		ret_val = BLE_STATUS_SUCCESS;
	return ret_val;
}

/**
 * @brief Handler for meta events
 * @param hci_meta_evt is the pointer to the data
 */
void meta_event_handler(evt_le_meta_event *hci_meta_evt) {
	// Connect on connection event, stop advertising
	if(hci_meta_evt->subevent == EVT_LE_CONN_COMPLETE) {
		evt_le_connection_complete *hci_con_comp_evt = (void*) hci_meta_evt->data;
		cb_on_gap_connection_complete(hci_con_comp_evt->peer_bdaddr, hci_con_comp_evt->handle);
	}
}

/**
 * @brief Handler for vendor events
 * @param vendor_evt is the pointer to the data
 */
void vendor_event_handler(evt_blue_aci *vendor_evt) {
	if (vendor_evt->ecode == EVT_BLUE_GATT_READ_PERMIT_REQ) {
		// Handle a read request
		evt_gatt_read_permit_req *read_pmt_req_evt = (void*) vendor_evt->data;
		cb_on_read_request(read_pmt_req_evt->attr_handle);
	} else if(vendor_evt->ecode == EVT_BLUE_GATT_ATTRIBUTE_MODIFIED) {
		// Handle a modify or notify request
		evt_gatt_attr_modified_IDB05A1 *attr_modified_evt =	(void*) vendor_evt->data;
		cb_on_attribute_modified(attr_modified_evt->attr_handle, attr_modified_evt->data_length, attr_modified_evt->att_data);
	}
}

/**
 * @brief Event handler on a BLE event, manages connections, advertising and handles read/write/notify requests
 * @param pData is the pointer to the BLE event
 */
void event_user_notify(void *pData) {
	hci_uart_pckt *hci_pkt = pData;
	hci_event_pckt *hci_evt_pkt = (void*) hci_pkt->data;

	if (hci_pkt->type != HCI_EVENT_PKT)
		return;

	if (hci_evt_pkt->evt == EVT_DISCONN_COMPLETE) {
			// Disconnect on disconnection event
			cb_on_gap_disconnection_complete();
	} else if(hci_evt_pkt->evt == EVT_LE_META_EVENT) {
			evt_le_meta_event *hci_meta_evt = (void*) hci_evt_pkt->data;
			meta_event_handler(hci_meta_evt);
	} else if(hci_evt_pkt->evt == EVT_VENDOR) {
		    evt_blue_aci *hci_event_vendor = (void*) hci_evt_pkt->data;
			vendor_event_handler(hci_event_vendor);
	}
}
