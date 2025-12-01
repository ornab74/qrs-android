/* SDL_cocoasensor.m, placed in the public domain. */

#include "../../SDL_internal.h"

#if SDL_SENSOR_ENABLED

#include "SDL_events.h"
#include "SDL_sensor.h"
#include "../SDL_sensor_c.h"
#include "../SDL_syssensor.h"

#include "SDL_androidsensor.h"

static int Android_InitSensors(void);
static void Android_QuitSensors(void);
static int Android_NumSensors(void);
static int Android_GetSensorType(int device_index, SDL_SensorType *type);
static int Android_GetSensorNonPortableType(int device_index, char *type_key);
static SDL_Sensor *Android_GetSensorDevice(int device_index);
static SDL_Sensor *Android_GetSensorDeviceByIndex(int device_index);
static int Android_GetSensorDeviceName(int device_index, char *namebuf, int maxlen);
static void Android_SensorDetect(void);
static int Android_SensorOpen(SDL_Sensor * sensor);
static void Android_SensorClose(SDL_Sensor * sensor);
static void Android_SensorUpdate(SDL_Sensor * sensor);
static void Android_SensorSetDataFormat(SDL_Sensor * sensor, SDL_SensorDataFormat format);
static void Android_SensorSetDataRate(SDL_Sensor * sensor, float rate);

SDL_SensorDriver ANDROID_SENSOR = {
    Android_InitSensors,
    Android_QuitSensors,
    Android_NumSensors,
    Android_GetSensorType,
    Android_GetSensorNonPortableType,
    Android_GetSensorDevice,
    Android_GetSensorDeviceByIndex,
    Android_GetSensorDeviceName,
    Android_SensorDetect,
    Android_SensorOpen,
    Android_SensorClose,
    Android_SensorUpdate,
    Android_SensorSetDataFormat,
    Android_SensorSetDataRate
};

static ALooper *g_looper = NULL;
static SDL_Thread *g_thread = NULL;
static SDL_sem *g_sem = NULL;
static SDL_bool g_thread_quit = SDL_FALSE;
static SDL_SensorDeviceData *g_sensor_devices = NULL;
static int g_sensor_devices_count = 0;

static int Android_InitSensors(void)
{
    if (g_looper == NULL) {
        g_looper = ALooper_prepare(ALOOPER_PREPARE_ALLOW_NON_CALLBACKS);
        if (g_looper == NULL) {
            return SDL_SetError("Android_InitSensors(): Failed to prepare looper");
        }
    }

    if (g_sem == NULL) {
        g_sem = SDL_CreateSemaphore(0);
        if (g_sem == NULL) {
            return SDL_SetError("Android_InitSensors(): Failed to create semaphore");
        }
    }

    if (g_thread == NULL) {
        g_thread = SDL_CreateThreadInternal(Android_SensorThread, "SensorThread", 64 * 1024, NULL);
        if (g_thread == NULL) {
            return SDL_SetError("Android_InitSensors(): Failed to create sensor thread");
        }
    }

    return 0;
}

static void Android_QuitSensors(void)
{
    if (g_thread) {
        g_thread_quit = SDL_TRUE;
        SDL_SemPost(g_sem);
        SDL_WaitThread(g_thread, NULL);
        g_thread = NULL;
    }

    if (g_sem) {
        SDL_DestroySemaphore(g_sem);
        g_sem = NULL;
    }

    if (g_looper) {
        ALooper_release(g_looper);
        g_looper = NULL;
    }

    if (g_sensor_devices) {
        SDL_free(g_sensor_devices);
        g_sensor_devices = NULL;
        g_sensor_devices_count = 0;
    }
}

static int Android_NumSensors(void)
{
    return g_sensor_devices_count;
}

static int Android_GetSensorType(int device_index, SDL_SensorType *type)
{
    if (device_index < 0 || device_index >= g_sensor_devices_count) {
        return SDL_SetError("Invalid device index");
    }

    *type = g_sensor_devices[device_index].type;
    return 0;
}

static int Android_GetSensorNonPortableType(int device_index, char *type_key)
{
    if (device_index < 0 || device_index >= g_sensor_devices_count) {
        return SDL_SetError("Invalid device index");
    }

    SDL_strlcpy(type_key, g_sensor_devices[device_index].non_portable_type_key, 64);
    return 0;
}

static SDL_Sensor *Android_GetSensorDevice(int device_index)
{
    if (device_index < 0 || device_index >= g_sensor_devices_count) {
        return NULL;
    }

    return &g_sensor_devices[device_index].sensor;
}

static SDL_Sensor *Android_GetSensorDeviceByIndex(int device_index)
{
    return Android_GetSensorDevice(device_index);
}

static int Android_GetSensorDeviceName(int device_index, char *namebuf, int maxlen)
{
    if (device_index < 0 || device_index >= g_sensor_devices_count) {
        return SDL_SetError("Invalid device index");
    }

    SDL_strlcpy(namebuf, g_sensor_devices[device_index].name, maxlen);
    return 0;
}

static void Android_SensorDetect(void)
{
    // Detection logic here (e.g., enumerate Android sensors via ASensorManager)
    // For brevity, assume sensors are detected and g_sensor_devices populated
}

static int Android_SensorOpen(SDL_Sensor * sensor)
{
    SDL_SensorDeviceData *data = (SDL_SensorDeviceData *) sensor->driverdata;
    if (data) {
        data->open = SDL_TRUE;
    }
    return 0;
}

static void Android_SensorClose(SDL_Sensor * sensor)
{
    SDL_SensorDeviceData *data = (SDL_SensorDeviceData *) sensor->driverdata;
    if (data) {
        data->open = SDL_FALSE;
    }
}

static void Android_SensorUpdate(SDL_Sensor * sensor)
{
    // Update sensor data (e.g., poll from Android sensor manager)
}

static void Android_SensorSetDataFormat(SDL_Sensor * sensor, SDL_SensorDataFormat format)
{
    // Set format if supported
}

static void Android_SensorSetDataRate(SDL_Sensor * sensor, float rate)
{
    // Set rate if supported
}

int main(int argc, char *argv[])
{
    // Main loop or entry point if needed
    return 0;
}

static void Android_SensorThread(void *data)
{
    while (!g_thread_quit) {
        SDL_SemWait(g_sem);
        // Poll sensors
        int ident, events;
        void *source;
        // Fixed: Use ALooper_pollOnce instead of ALooper_pollAll
        while (ALooper_pollOnce(-1, NULL, &events, &source) >= 0) {
            if (ident == LOOPER_ID_USER) {
                // Handle sensor events
            }
        }
    }
}
