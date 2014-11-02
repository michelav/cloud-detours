package br.unifor.ppgia.cloud.core.comm;

import static org.junit.Assert.*;

import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;

import br.unifor.ppgia.cloud.core.comm.ChannelProvider.EventType;

public class EventTests {

	String header = "{\"control\":\"ping\",\"msg\":\"test\"}";

	@BeforeClass
	public static void setUpBeforeClass() throws Exception {
	}

	@AfterClass
	public static void tearDownAfterClass() throws Exception {
	}

	@Before
	public void setUp() throws Exception {
	}

	@After
	public void tearDown() throws Exception {
	}

	@Test
	public void testWire() {
		ChannelProvider provider = ChannelProvider.getInstance();
		Event event = provider.getEvent(EventType.PING_EVT);
		event.addInfo("msg", "test");
		String wire = event.wire();

		assertEquals(
				"Malformed JSON String. '{' should be the first element...",
				0 , wire.indexOf("{"));
		assertEquals(
				"Malformed JSON String. '}' should be the last element...",
				wire.length() - 1, wire.indexOf("}"));
		assertEquals("control:ping doesnt exists in wired String...",
				true, wire.indexOf("\"control\":\"ping\"")>-1);
		assertEquals("control:ping doesnt exists in wired String...",
				true, wire.indexOf("\"msg\":\"test\"")>-1);
	}

	@Test
	public void testLoadMetaData() {
		ChannelProvider provider = ChannelProvider.getInstance();
		Event event = provider.getEvent(EventType.BLANK_EVT);
		event.loadMetaData(header);

		assertEquals("loadMetaData didn't work properly...", "ping",
				event.getInfo("control"));
		assertEquals("loadMetaData didn't work properly...", "test",
				event.getInfo("msg"));
	}
}
