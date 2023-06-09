# Storage System

## Physical Storage Media

#### Persistent of Storage Media
- Volatile : Data is lost when power is off
- Non-Volatile : Data is retained when power is off
  - Note that is **not safe** on system crash
- Stable Storage : Data is **never** lost
  - Just theoretical concept
  - Implement with multiple copies of data

#### Hierarchical Storage
- Primary Storage : volatile storage
  - CPU Registers
  - Cache
  - Main Memory
- Secondary Storage : on-line storage, non-volatile storage
  - Magnetic Disks(HDD)
  - Flash Memory
  - Solid State Drives(SSD)
- Tertiary Storage : off-line storage, non-volatile storage
  - Optical Disks(CD, DVD, Blu-ray)
  - Magnetic Tapes

## Magnetic Disks

#### Components
- Platters
  - Divided into tracks : concentric circles
  - Each track is divided into sectors : pie-shaped wedges
- Arms
  - Each arm has a head
  - Each head can read/write one track at a time
    - Head read/write data using magnet
- Hard Disck Assembly
  - Normally, multiple platters are stacked on a disk
  - All heads are attached to a single arm and each head used to read/write one platter

#### Performance
- Access Time
  - Seek Time : time delay for move arm vertically
    - Average seek time is half of the maximum seek time
    - Maximum seek time is the time to move the arm from the outermost track to the innermost track
  - Rotational Latency : time delay for rotate disk
    - Average rotational latency is half of the maximum rotational latency
    - Maximum rotational latency is the time to wait for a full rotation of the disk
- Data Transfer Rate
  - Rate at which data can be read from or written to the disk
  - Depends on the rotational speed of the disk and the data density
- Mean Time to Failure(MTTF)
  - Average time between disk failures
  - Usually 1 million hours

#### Optimizing Disk Performance

## RAID(Redundant Array of Independent Disks)

#### Overview
- Reliability via redundancy
  - Mirroring
    - Write to multiple disks
    - Read from any disk
  - Parity : information about the data for recover corrupted data
    - store parity information on a separate disk

- Performance via parallelism
  - Block-level striping : divide data into blocks and store each block on a different disk
    - Read/Write data in parallel

#### RAID 0
- Block-level striping
- Danger in system crash
  - If one disk fails, all data is lost
#### RAID 1
- RAID 0 + Mirroring
  - Best write performance
#### RAID 5
- Block-level striping + Parity
  - Parity information is distributed across all disks
- Via RAID1
  - lower storage overhead
  - lower write performance
  - good for frequent read, rare write