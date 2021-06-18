/*
 * services.h
 *
 *  Created on: Mar 2, 2021
 *  Author: Silvano Cortesi
 */

#ifndef INC_SERVICES_H_
#define INC_SERVICES_H_

#ifdef __cplusplus
extern "C" {
#endif

#include "bluenrg_def.h"

/**
 * Initialization functions for the different services
 * @return tBleStatus, indicating an error. BLE_STATUS_SUCCESS on success.
 */
tBleStatus add_services();

#ifdef __cplusplus
}
#endif

#endif /* INC_SERVICES_H_ */
