################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (9-2020-q2-update)
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include Middlewares/ST/BlueNRG-MS/utils/subdir.mk
-include Middlewares/ST/BlueNRG-MS/hci/hci_tl_patterns/Basic/subdir.mk
-include Middlewares/ST/BlueNRG-MS/hci/controller/subdir.mk
-include Middlewares/ST/BlueNRG-MS/hci/subdir.mk
-include Drivers/STM32L4xx_HAL_Driver/Src/subdir.mk
-include Drivers/BLE/Src/BLE_Services/subdir.mk
-include Drivers/BLE/Src/subdir.mk
-include Core/Startup/subdir.mk
-include Core/Src/subdir.mk
-include BlueNRG_MS/Target/subdir.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(S_DEPS)),)
-include $(S_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

OPTIONAL_TOOL_DEPS := \
$(wildcard ../makefile.defs) \
$(wildcard ../makefile.init) \
$(wildcard ../makefile.targets) \


BUILD_ARTIFACT_NAME := BLE_Test_Silvano
BUILD_ARTIFACT_EXTENSION := elf
BUILD_ARTIFACT_PREFIX := 
BUILD_ARTIFACT := $(BUILD_ARTIFACT_PREFIX)$(BUILD_ARTIFACT_NAME).$(BUILD_ARTIFACT_EXTENSION)

# Add inputs and outputs from these tool invocations to the build variables 
EXECUTABLES += \
BLE_Test_Silvano.elf \

SIZE_OUTPUT += \
default.size.stdout \

OBJDUMP_LIST += \
BLE_Test_Silvano.list \

OBJCOPY_BIN += \
BLE_Test_Silvano.bin \


# All Target
all: main-build

# Main-build Target
main-build: BLE_Test_Silvano.elf secondary-outputs

# Tool invocations
BLE_Test_Silvano.elf: $(OBJS) $(USER_OBJS) C:\Users\Jacki\Documents\Problemathiker\STM_Workspace\BLE_Test_Silvano\STM32L476JGYX_FLASH.ld makefile objects.list $(OPTIONAL_TOOL_DEPS)
	arm-none-eabi-gcc -o "BLE_Test_Silvano.elf" @"objects.list" $(USER_OBJS) $(LIBS) -mcpu=cortex-m4 -T"C:\Users\Jacki\Documents\Problemathiker\STM_Workspace\BLE_Test_Silvano\STM32L476JGYX_FLASH.ld" --specs=nosys.specs -Wl,-Map="BLE_Test_Silvano.map" -Wl,--gc-sections -static --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -Wl,--start-group -lc -lm -Wl,--end-group
	@echo 'Finished building target: $@'
	@echo ' '

default.size.stdout: $(EXECUTABLES) makefile objects.list $(OPTIONAL_TOOL_DEPS)
	arm-none-eabi-size  $(EXECUTABLES)
	@echo 'Finished building: $@'
	@echo ' '

BLE_Test_Silvano.list: $(EXECUTABLES) makefile objects.list $(OPTIONAL_TOOL_DEPS)
	arm-none-eabi-objdump -h -S $(EXECUTABLES) > "BLE_Test_Silvano.list"
	@echo 'Finished building: $@'
	@echo ' '

BLE_Test_Silvano.bin: $(EXECUTABLES) makefile objects.list $(OPTIONAL_TOOL_DEPS)
	arm-none-eabi-objcopy  -O binary $(EXECUTABLES) "BLE_Test_Silvano.bin"
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) *
	-@echo ' '

secondary-outputs: $(SIZE_OUTPUT) $(OBJDUMP_LIST) $(OBJCOPY_BIN)

fail-specified-linker-script-missing:
	@echo 'Error: Cannot find the specified linker script. Check the linker settings in the build configuration.'
	@exit 2

warn-no-linker-script-specified:
	@echo 'Warning: No linker script specified. Check the linker settings in the build configuration.'

.PHONY: all clean dependents fail-specified-linker-script-missing warn-no-linker-script-specified
.SECONDARY:

-include ../makefile.targets
