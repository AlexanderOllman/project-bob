# Samples APIs

## General usage

Once the server starts to run[make serve] the follwing curls can be executed. 
All exampl curls are pointing to localhost, modify the curls beased on appropriate host details

### health check
```bash
curl --location 'http://127.0.0.1:8000/api/health'
```

#### Response for health check
```
{
    "Response": "I am healthy"
}
```
### chat request without history
```bash
curl --location 'http://localhost:8000/api/chat' \
--header 'Content-Type: application/json' \
--data '{
    "message": "in ezmeral 2012-07-31 04:43:50,716 ERROR com.mapr.baseutils.cldbutils.CLDBRpcCommonUtils [VolumeMirrorThread]: Unable to reach cluster with name: qacluster1.2.9. No entry found in file /conf/mapr-clusters.conf for cluster qacluster1.2.9. Failing the CLDB RPC with status 133"
    }'
```
#### Response for chat request without history
```
{
    "bot_response": "1. The error message indicates that there is an issue with reaching the cluster named \"qacluster1.2.9\" in the MapR environment.\n2. The specific error \"No entry found in file /conf/mapr-clusters.conf for cluster qacluster1.2.9\" suggests that the configuration file mapr-clusters.conf does not have an entry for the mentioned cluster.\n3. As a result of not finding the cluster entry in the configuration file, the CLDB RPC (Control Node RPC) fails with status 133, indicating a failure in the communication with the cluster.\n4. To resolve this issue, you need to ensure that the cluster configuration file (/conf/mapr-clusters.conf) contains the correct entry for \"qacluster1.2.9\" with the necessary details such as IP address, port, and other configuration parameters to establish the connection successfully.",
    "chat_history": "Human: in ezmeral 2012-07-31 04:43:50,716 ERROR com.mapr.baseutils.cldbutils.CLDBRpcCommonUtils [VolumeMirrorThread]: Unable to reach cluster with name: qacluster1.2.9. No entry found in file /conf/mapr-clusters.conf for cluster qacluster1.2.9. Failing the CLDB RPC with status 133\nAI: 1. The error message indicates that there is an issue with reaching the cluster named \"qacluster1.2.9\" in the MapR environment.\n2. The specific error \"No entry found in file /conf/mapr-clusters.conf for cluster qacluster1.2.9\" suggests that the configuration file mapr-clusters.conf does not have an entry for the mentioned cluster.\n3. As a result of not finding the cluster entry in the configuration file, the CLDB RPC (Control Node RPC) fails with status 133, indicating a failure in the communication with the cluster.\n4. To resolve this issue, you need to ensure that the cluster configuration file (/conf/mapr-clusters.conf) contains the correct entry for \"qacluster1.2.9\" with the necessary details such as IP address, port, and other configuration parameters to establish the connection successfully.",
    "question_summary": "Error reaching cluster qacluster1.2.9, status 133.",
    "answer_context": []
}
```
### chat request with conversation history
```bash
curl --location 'http://localhost:8000/api/chat' \
--header 'Content-Type: application/json' \
--data '{
    "message": "In HPE Ezmeral explain the steps for connecting to Ray Cluster in full detail?",
    "chat_history": "System: The human asks for a detailed explanation of how to disconnect from a Ray Cluster in HPE Ezmeral. The AI provides step-by-step instructions, including disabling GPU support for Ray and disconnecting from the cluster either within the software or from outside. By following these steps, users can properly disconnect from a Ray Cluster in HPE Ezmeral Unified Analytics Software."
}'
```
#### Response for chat request with conversation history
```{
    "bot_response": "1. **Connecting to Ray in HPE Ezmeral Unified Analytics Software**:\n   - Run the following command: `ray.init(address=\"ray://kuberay-head-svc.kuberay:10001\")`.\n\n2. **Connecting to Ray from outside of HPE Ezmeral Unified Analytics Software**:\n   - Change the service type to NodePort by running: `kubectl -n kuberay edit service kuberay-head-svc`.\n   - Obtain the cluster master IP by running: `kubectl cluster-info`.\n   - Get the client port by running: `kubectl -n kuberay describe service kuberay-head-svc`.\n   - Connect using `<K8 Master IP>:<Client Port>` with the command: `ray.init(address=\"ray://<K8 Master IP>:31536\")`.",
    "chat_history": "System: System: The human asks for a detailed explanation of how to disconnect from a Ray Cluster in HPE Ezmeral. The AI provides step-by-step instructions, including disabling GPU support for Ray and disconnecting from the cluster either within the software or from outside. By following these steps, users can properly disconnect from a Ray Cluster in HPE Ezmeral Unified Analytics Software.\nHuman: Can you provide step-by-step instructions for connecting to a Ray Cluster in HPE Ezmeral Unified Analytics Software?\nAI: 1. **Connecting to Ray in HPE Ezmeral Unified Analytics Software**:\n   - Run the following command: `ray.init(address=\"ray://kuberay-head-svc.kuberay:10001\")`.\n\n2. **Connecting to Ray from outside of HPE Ezmeral Unified Analytics Software**:\n   - Change the service type to NodePort by running: `kubectl -n kuberay edit service kuberay-head-svc`.\n   - Obtain the cluster master IP by running: `kubectl cluster-info`.\n   - Get the client port by running: `kubectl -n kuberay describe service kuberay-head-svc`.\n   - Connect using `<K8 Master IP>:<Client Port>` with the command: `ray.init(address=\"ray://<K8 Master IP>:31536\")`.",
    "answer_context": [
        "https://d2cel7q09kz0pe.cloudfront.net/Ezmeral/Ezmeral_Unified_Analytics_13_documentation.pdf#page=123",
        "https://d2cel7q09kz0pe.cloudfront.net/Ezmeral/Ezmeral_Unified_Analytics_13_documentation.pdf#page=65",
        "https://d2cel7q09kz0pe.cloudfront.net/Ezmeral/Ezmeral_Unified_Analytics_13_documentation.pdf#page=194",
        "https://d2cel7q09kz0pe.cloudfront.net/Ezmeral/Ezmeral_Unified_Analytics_13_documentation.pdf#page=333",
        "https://d2cel7q09kz0pe.cloudfront.net/Ezmeral/Ezmeral_Unified_Analytics_13_documentation.pdf#page=338",
        "https://d2cel7q09kz0pe.cloudfront.net/Ezmeral/Ezmeral_Unified_Analytics_13_documentation.pdf#page=334"
    ]
}
```

### Event Iterpretataion with a log message
```bash
curl --location 'http://127.0.0.1:8000/api/log-analysis' \
--header 'Content-Type: application/json' \
--data '{
    "log": "interpret this cassandra log 2023-11-15 00:37:30,481 host:  cassandra-host-1234 level: warn source:  cassandra message: GCInspector.java:285  - ParNew GC in 325ms. CMS Old Gen:  330043632 -> 330516960; Pa Eden Space: 167772160 -> 0; Par Survivor Space: 753024 -> 784776"
}
```
#### Response for Event Iterpretataion with a log message
```{
    "log_analysis": "This log entry indicates that a ParNew garbage collection event occurred on the Cassandra host \"cassandra-host-1234\" at the timestamp 2023-11-15 00:37:30. The event took 325ms to complete and involved the following memory usage changes:\n- CMS Old Gen: 330043632 -> 330516960\n- Par Eden Space: 167772160 -> 0\n- Par Survivor Space: 753024 -> 784776\n\nThe warning level suggests that the garbage collection event may have caused some performance impact on the system. The increase in Old Gen memory usage may indicate that the system is not able to reclaim memory efficiently, potentially leading to memory leaks or increased memory pressure.\n\nTo resolve this issue, you can consider the following steps:\n1. Tune the JVM garbage collection settings to optimize memory management. You may need to adjust the heap size, garbage collection algorithms, and other parameters to better suit the workload of your Cassandra cluster.\n2. Monitor the memory usage and garbage collection events regularly to identify any patterns or anomalies that may indicate underlying issues.\n3. Investigate any potential memory leaks in the application code or Cassandra configuration that could be contributing to the increased memory usage.\n4. Consider upgrading the hardware or scaling out the Cassandra cluster to distribute the workload and reduce memory pressure on individual nodes.\n\nBy addressing these potential causes and optimizing the memory management settings, you can help prevent performance issues related to garbage collection events in Cassandra."
}
```
