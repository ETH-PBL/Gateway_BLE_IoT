/*
 * app_ble.h
 *
 *  Created on: Mar 2, 2021
 *  Author: Silvano Cortesi
 */

#ifndef INC_APP_BLE_H_
#define INC_APP_BLE_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "bluenrg_def.h"

// Set Public BLE device address to a unique value, use 6 bytes
#define BLUETOOTH_DEVICE_ADDRESS { 0xAA, 0xBB, 0xCC, 0x09, 0x12, 0x13 }
#define BLUETOOTH_DEVICE_ADDRESS_SIZE 6

// Set a device name for the peripheral, set its size without the termination character (i.e. number of REAL characters)
#define DEVICE_NAME "CounterTester"
#define DEVICE_NAME_SIZE 13	// without termination character

/**
 * @brief Function to initialize BLE
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus MX_BlueNRG_MS_Init(void);

/**
 * @brief Process BLE events and send notifications
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus MX_BlueNRG_MS_Process(void);

/**
 * @brief Function to set the device into connectable mode
 */
void set_connectable_status(void);

/**
 * @brief Function to clear the connectable mode, stops advertising and starts the GATT server
 */
void clear_connectable_status(void);

#ifdef __cplusplus
}
#endif

#endif /* INC_APP_BLE_H_ */
