package com.pragatix.repository;

import com.pragatix.entity.SecurityAuditLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface SecurityAuditLogRepository extends JpaRepository<SecurityAuditLog, Long> {

    List<SecurityAuditLog> findByUsername(String username);

    List<SecurityAuditLog> findByEventType(String eventType);

    List<SecurityAuditLog> findByTimestampBetween(LocalDateTime start, LocalDateTime end);
}
