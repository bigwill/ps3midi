#include <stdio.h>
#include <wchar.h>
#include <string.h>
#include <stdlib.h>
#include "hidapi.h"

#include <unistd.h>

#define EXPORT __attribute__((visibility("default")))

// Based on http://wiki.ps2dev.org/ps3:hardware:sixaxis
typedef struct {
  char hid_channel;
  char unknown1;
  char button_states[3];
  char unknown2;
  char left_analog_horiz;
  char left_analog_vert;
  char right_analog_horiz;
  char right_analog_vert;
  char unknown_axes[4];
  char button_pressures[12];
  char unknown3[3];
  char status;
  char power_rating;
  char status2;
  char unknown4[9];
  char accelerator[6];
  char z_gyro[2];
} ps3_state;

EXPORT
hid_device *ps3_open()
{
  // Open the device using the VID, PID,
  // and optionally the Serial number.
  return hid_open(0x54c, 0x0268, NULL);
}

EXPORT
void ps3_close(hid_device *h)
{
  hid_close(h);
}

EXPORT
int ps3_read(hid_device *h, unsigned char *s)
{
  unsigned char buf[256];

  memset(buf, 0x00, sizeof(buf));
  // Request state (cmd 0x81). The first byte is the report number (0x1).
  buf[0] = 0x1;
  buf[1] = 0x81;

  int res = hid_write(h, buf, 17);
  if (res < 0)
    return res;

  res = hid_read(h, (unsigned char*)s, sizeof(ps3_state));
  if (res <= 0)
    memset(s, 0x00, sizeof(ps3_state));
  return res;
}
