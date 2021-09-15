#ifndef PACKING_RAWDATAFILE_EVENTPACKET_H_
#define PACKING_RAWDATAFILE_EVENTPACKET_H_

#include <iostream>
#include <string>
#include <vector>

#include "Packing/RawDataFile/SubsystemPacket.h"

namespace packing {
namespace rawdatafile {

/**
 * Event Packet structure
 */
class EventPacket {
 public:
  EventPacket() = default;
  ~EventPacket() = default;

  /**
   * read a packet from the input stream
   */
  void read(utility::Reader& r);

  /// Get subsystem data
  const std::vector<SubsystemPacket>& get() const {
    return subsys_data_;
  }

  /**
   * write a packet to the output stream
  void write(std::ostream& os);
   */

  /**
   * Insert some subsystem data
  void insert(const SubsystemPacket& data) {
    subsys_data_.emplace_back(data);
  }
   */

 private:
  unsigned int event_id_;
  unsigned int num_subsystems_;
  bool crc_ok_;
  unsigned int event_length_in_words_;
  uint32_t crc_;
  std::vector<SubsystemPacket> subsys_data_;
};  // EventPacket

}  // namespace rawdatafile
}  // namespace packing

#endif  // PACKING_RAWDATAFILE_EVENTPACKET_H_