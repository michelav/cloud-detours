package br.unifor.ppgia.cloud.core.comm.defaultimpl;

import java.lang.reflect.Type;
import java.util.Map;

import br.unifor.ppgia.cloud.core.comm.Event;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

public class DefaultIOEvent extends Event {

	public DefaultIOEvent() {
		super();
	}

	public DefaultIOEvent(Map<String, String> md, byte[] data) {
		super(md, data);
	}

	public DefaultIOEvent(Map<String, String> md) {
		super(md);
	}

	@Override
	public String wire() {
		Gson gson = new Gson();
		return gson.toJson(getMetaData());
	}

	@Override
	public void loadMetaData(String headers) {
		Gson gson = new Gson();
		Type stringStringMap = new TypeToken<Map<String, String>>() {
		}.getType();
		Map<String, String> md = gson.fromJson(headers, stringStringMap);
		setMetaData(md);
	}

	@Override
	public void setPayload(byte[] payload) {
		if (payload != null) {
			super.setPayload(payload);
			addInfo("payload", "True");
		}
	}
}
