package br.unifor.ppgia.cloud.core.comm;

import java.util.HashMap;
import java.util.Map;

public abstract class Event {
	
	
	private Map<String, String> metaData;
	
	private byte[] payload;
	
	public Event() {
		metaData = new HashMap<String, String>();
		metaData.put("payload", "False");
	}
	
	public Event(Map<String, String> md) {
		metaData = md;
		metaData.put("payload", "False");
	}
	
	public Event(Map<String, String> md, byte[] data) {
		metaData = md;
		setPayload(data);
	}
	
	public void addInfo(String key, String data) {
		metaData.put(key, data);
	}
	
	public void addInfo(Map<String, String> headers) {
		metaData.putAll(headers);
	}
	
	public void removeInfo(String key) {
		metaData.remove(key);
	}
	
	public String getInfo(String key) {
		return metaData.get(key);
	}
	
	public Map<String, String> getMetaData() {
		return metaData;
	}
	
	public void setMetaData(Map<String, String> md) {
		metaData = md;
	}
	
	public byte[] getPayload() {
		return payload;
	}

	public void setPayload(byte[] payload) {
		if(payload != null) {
			this.payload = payload;
			addInfo("payload", "True");
		}
	}
	
	public abstract String wire();
	
	public abstract void loadMetaData(String headers);
}

