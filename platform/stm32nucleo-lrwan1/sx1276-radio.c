#include "contiki.h"
#include "net/netstack.h"

static int sx1276_radio_init(void) { return 0; }
static int sx1276_radio_prepare(const void *payload, unsigned short payload_len) { return 0; };
static int sx1276_radio_transmit(unsigned short payload_len) { return 0; };
static int sx1276_radio_send(const void *data, unsigned short len) { return 0; };
static int sx1276_radio_read(void *buf, unsigned short bufsize) { return 0; };
static int sx1276_radio_channel_clear(void) { return 0; };
static int sx1276_radio_receiving_packet(void) { return 0; };
static int sx1276_radio_pending_packet(void) { return 0; };
static int sx1276_radio_on(void) { return 0; };
static int sx1276_radio_off(void) { return 0; };
/*---------------------------------------------------------------------------*/
const struct radio_driver sx1276_radio_driver =
{
  sx1276_radio_init,
  sx1276_radio_prepare,
  sx1276_radio_transmit,
  sx1276_radio_send,
  sx1276_radio_read,
  sx1276_radio_channel_clear,
  sx1276_radio_receiving_packet,
  sx1276_radio_pending_packet,
  sx1276_radio_on,
  sx1276_radio_off,
};

